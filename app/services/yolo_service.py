import os
import cv2
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Union, Optional
from tqdm import tqdm
from datetime import datetime
from ultralytics import YOLO

from app.configuration.config import settings
from app.tasks.taskfiles.image_task import compress_processed_image_task
from app.utils.logger import log


class YOLOProcessor:
    def __init__(
        self,
        config: dict,
        model_size: str = "small",
        model_types: Optional[list] = None,
    ):
        """
        Initialize YOLO models with configuration

        Args:
            config (dict): Configuration containing model paths and parameters
            model_size (str): Size of models to load ('nano', 'small', 'medium', 'large', 'extreme')
            model_types (list, optional): List of model types to load ('detection', 'segmentation',
                                        'classification', 'pose'). If None, loads all types.
        """
        self.base_dir = Path(config["base_dir"])
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Validate model size
        size_key = f"{model_size}_models"
        if size_key not in config:
            raise ValueError(
                f"Invalid model size: {model_size}. Must be one of: "
                f"{[key.split('_')[0] for key in config.keys() if key.endswith('_models')]}"
            )

        # Get model configuration for specified size
        self.model_config = config[size_key]
        self.models: Dict[str, YOLO] = {}

        # Create model directory if it doesn't exist
        self.model_dir = self.base_dir / self.model_config["path"].strip("/")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        os.environ["YOLO_CONFIG_DIR"] = str(self.model_dir)

        # Load specified model types or all available types
        model_types = model_types or self.model_config["models"].keys()
        self._load_models(model_types)
        log.info(
            f"Initialized YOLOProcessor with {model_size} models\nModel description: {self.model_config['description']}\nExpected inference speed: {self.model_config['speed']}"
        )

    def _load_models(self, model_types: list) -> None:
        """
        Load multiple YOLO models based on configuration

        Args:
            model_types (list): List of model types to load
        """
        for model_type in model_types:
            if model_type not in self.model_config["models"]:
                log.warning(
                    f"Model type '{model_type}' not found in configuration. Skipping."
                )
                continue

            try:
                model_file = self.model_config["models"][model_type]
                model_path = self.model_dir / model_file

                if not model_path.exists():
                    log.info(
                        f"Model not found locally. Downloading {model_file} to {self.model_dir}"
                    )

                self.models[model_type] = YOLO(str(model_path))
                log.info(f"Successfully loaded {model_type} model from {model_path}")

            except Exception as e:
                log.error(f"Failed to load {model_type} model: {str(e)}")
                raise

    def train_model(
        self,
        model_type: str,
        data_path: str,
        epochs: int = 100,
        batch_size: int = 16,
        imgsz: int = 640,
        **kwargs,
    ) -> None:
        """
        Train a specific YOLO model

        Args:
            model_type: Type of model to train ('detection', 'segmentation', etc.)
            data_path: Path to data configuration file
            epochs: Number of training epochs
            batch_size: Training batch size
            imgsz: Input image size
        """
        if model_type not in self.models:
            raise ValueError(f"Model type {model_type} not found")

        try:
            log.info(f"Starting training for {model_type} model")
            self.models[model_type].train(
                data=data_path,
                epochs=epochs,
                batch_size=batch_size,
                imgsz=imgsz,
                device=self.device,
                **kwargs,
            )
            log.info(f"Completed training for {model_type} model")

        except Exception as e:
            log.error(f"Training failed: {str(e)}")
            raise

    def _extract_results(self, results, model_type: str) -> List[Dict]:
        """Extract relevant information from model results based on model type"""
        if model_type in ["detection", "segmentation"]:
            return [
                {
                    "class_name": results[0].names[int(cls)],
                    "confidence": float(conf),
                    "bbox": box[:4].tolist(),
                }
                for box, cls, conf in zip(
                    results[0].boxes.data, results[0].boxes.cls, results[0].boxes.conf
                )
            ]

        elif model_type == "classification":
            # Classification provides predictions for the whole image
            top5_indices = results[0].probs.top5
            return [{
                "primary_class": {
                    "class_name": results[0].names[int(top5_indices[0])],
                    "confidence": float(results[0].probs.top1conf),
                },
                "top_5_predictions": [
                    {
                        "class_name": results[0].names[int(idx)],
                        "confidence": float(results[0].probs.data[idx]),
                    }
                    for idx in top5_indices
                ],
            }]

        elif model_type == "pose":
            return [
                {
                    "class_name": (
                        results[0].names[int(class_label)]
                        if (class_label is not None and results[0].names is not None)
                        else None
                    ),
                    "confidence": float(conf),
                    "bbox": box[:4].tolist(),
                    "keypoints": kpts.tolist() if kpts is not None else None,
                }
                for box, conf, kpts, class_label in zip(
                    results[0].boxes.data,
                    results[0].boxes.conf,
                    (
                        results[0].keypoints.data
                        if results[0].keypoints is not None
                        else [None] * len(results[0].boxes)
                    ),
                    results[0].boxes.cls if hasattr(results[0].boxes, "cls") else None,
                )
            ]
        return {}

    def _count_objects(self, results, model_type: str) -> int:
        """Count the number of detected objects/classes based on model type"""
        if model_type == "classification":
            return 1
        elif hasattr(results[0], "boxes"):
            return len(results[0].boxes)
        return 0

    def process_image(
        self,
        file_name: str,
        image_path: Union[str, Path],
        model_type: str = "detection",
        save_results: bool = True,
        conf: float = 0.25,
    ) -> Dict:
        """
        Process a single image with specified model type

        Args:
            image_path (Union[str, Path]): Path to input image
            model_type (str): Type of model to use ('detection', 'segmentation', 'classification', 'pose')
            save_results (bool): Whether to save results
            conf (float): Confidence threshold for predictions
            output_dir (Optional[Union[str, Path]]): Custom output directory. If None, uses default structure
            batch_processing (bool): Whether this is part of batch processing (affects output directory structure)

        Returns:
            Dict: Processed results including predictions, processing time, and metadata

        Raises:
            ValueError: If model_type is not available
            FileNotFoundError: If image_path doesn't exist
            Exception: For other processing errors
        """
        try:
            # Convert image path to Path object
            if type(image_path) != Path:
                image_path = Path(image_path)

            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            # Validate model type
            if model_type not in self.models:
                raise ValueError(
                    f"Model type '{model_type}' not available. Available types: {list(self.models.keys())}"
                )

            # Process image
            log.info(f"Processing image: {image_path} with {model_type} model")
            start_time = datetime.now()
            output_dir = Path("output") / f"{model_type}_results"

            results = self.models[model_type](
                str(image_path),
                conf=conf,
                save=save_results,
                project=output_dir,
                name=".",
                exist_ok=True,
            )

            processed_image_path = Path(output_dir, image_path.stem)
            compress_processed_image_task.delay(
                image_path=str(processed_image_path),
                output_dir=str(output_dir),
                quality=50,
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            # Extract and format results
            processed_results = {
                "image_path": str(image_path),
                "image_url": None,
                "model_type": model_type,
                "processing_time": processing_time,
                "model_size": self.model_config["path"].strip("/"),
                "confidence_threshold": conf,
                "device": self.device,
                "predictions": self._extract_results(results, model_type),
                "output_path": str(Path(processed_image_path).with_suffix('.webp')),
                "total_objects": self._count_objects(results, model_type),
            }

            log.info(
                f"Successfully processed {image_path.name} in {processing_time:.2f} seconds\nFound {processed_results['total_objects']} {'objects' if model_type != 'classification' else 'class predictions'}"
            )
            return processed_results

        except Exception as e:
            log.error(f"Failed to process image {image_path}: {str(e)}")
            raise

    def process_video(
        self,
        video_path: Union[str, Path],
        model_type: str = "detection",
        batch_size: int = 32,
    ) -> List[Dict]:
        """
        Process video with batched frame processing for efficiency

        Args:
            video_path: Path to input video
            model_type: Type of model to use
            batch_size: Number of frames to process in each batch
        """
        frames_data = []
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        try:
            with tqdm(total=total_frames, desc="Processing video frames") as pbar:
                while cap.isOpened():
                    frames_batch = []
                    for _ in range(batch_size):
                        ret, frame = cap.read()
                        if not ret:
                            break
                        frames_batch.append(frame)

                    if not frames_batch:
                        break

                    # Process batch of frames
                    results = self.models[model_type](frames_batch)
                    frames_data.extend(self.extract_results(results))
                    pbar.update(len(frames_batch))

        finally:
            cap.release()

        return frames_data


# Model configuration
config = {
    "base_dir": f"{settings.BASE_DIR}/ML_models/yolo11",
    "nano_models": {
        "path": "/nano_models",
        "description": "Low accuracy, fastest model, optimized for low-power devices (mobile, edge computing).",
        "speed": "(~2-3 ms)",
        "models": {
            "detection": "yolo11n.pt",
            "segmentation": "yolo11n-seg.pt",
            "classification": "yolo11n-cls.pt",
            "pose": "yolo11n-pose.pt",
        },
    },
    "small_models": {
        "path": "/small_models",
        "description": "Fast object detection with good accuracy, offers a balance between speed and accuracy.",
        "speed": "(~3-5 ms)",
        "models": {
            "detection": "yolo11s.pt",
            "segmentation": "yolo11s-seg.pt",
            "classification": "yolo11s-cls.pt",
            "pose": "yolo11s-pose.pt",
        },
    },
    "medium_models": {
        "path": "/medium_models",
        "description": "Balanced accuracy and speed, offers a balance between speed and accuracy.",
        "speed": "(~8-15 ms)",
        "models": {
            "detection": "yolo11m.pt",
            "segmentation": "yolo11m-seg.pt",
            "classification": "yolo11m-cls.pt",
            "pose": "yolo11m-pose.pt",
        },
    },
    "large_models": {
        "path": "/large_models",
        "description": "High accuracy, server-side inference, suitable for high-accuracy tasks but require more computing power.",
        "speed": "(~15-25 ms)",
        "models": {
            "detection": "yolo11l.pt",
            "segmentation": "yolo11l-seg.pt",
            "classification": "yolo11l-cls.pt",
            "pose": "yolo11l-pose.pt",
        },
    },
    # "extreme_models": {
    #     "path": "/extreme_models",
    #     "description": "Best accuracy, heavy compute tasks, suitable for high-accuracy tasks but require more computing power.",
    #     "speed": "(~25-40 ms)",
    #     "models": {
    #         "detection": "yolo11x.pt",
    #         "segmentation": "yolo11x-seg.pt",
    #         "classification": "yolo11x-cls.pt",
    #         "pose": "yolo11x-pose.pt",
    #     },
    # }
}
