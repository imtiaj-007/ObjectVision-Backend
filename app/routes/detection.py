import json
import uuid
from typing import Dict, Any, Optional, Union, List
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from cache import local_storage
from cache.activity_tracker import user_activity_tracker
from app.db.database import db_session_manager
from app.services.auth_service import AuthService
from app.services.detection_service import DetectionService
from app.repository.user_activity_repository import UserActivityRepository
from app.tasks.taskfiles.subscription_task import update_user_activity_task

from app.schemas.enums import ModelSizeEnum, WebSocketMessageType, ActivityTypeEnum, DetectionTypeEnum
from app.schemas.detection_schema import DetectionRequest, DetectionResults, DetectionWithCount
from app.schemas.user_schema import UserData
from app.configuration.config import settings
from app.utils.logger import log


router = APIRouter()


async def validate_usage_limit(
    session: AsyncSession,
    user_data: UserData,
    detection_type: DetectionTypeEnum
) -> Dict[str, Any]:
    """ Method for checking user activity, usage and limits """
    try:
        # Check if user activity exists in cache
        cached_activities = user_activity_tracker.get_activities(user_data.username)

        # If not in cache or cache is incomplete, fetch from database
        if not cached_activities or not all(activity_type in cached_activities for activity_type in 
            [ActivityTypeEnum.IMAGE_USAGE, ActivityTypeEnum.VIDEO_USAGE, ActivityTypeEnum.STORAGE_USAGE]):

            active_plan = await UserActivityRepository.get_current_active_plan(
                db=session, user_id=user_data.id
            )            
            if not active_plan:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have any active plan, Please purchase a plan to continue."
                )

            # Determine which activity type to fetch based on detection type
            if detection_type == DetectionTypeEnum.IMAGE:
                main_activity = await UserActivityRepository.get_activity_by_plan_and_type(
                    db=session,
                    active_user_plan_id=active_plan.id,
                    activity_type=ActivityTypeEnum.IMAGE_USAGE,
                )
            else:
                main_activity = await UserActivityRepository.get_activity_by_plan_and_type(
                    db=session,
                    active_user_plan_id=active_plan.id,
                    activity_type=ActivityTypeEnum.VIDEO_USAGE,
                )

            # Cache the fetched activity
            user_activity_tracker.store_activity(user_data.username, main_activity)

            # Fetch storage activity
            storage_activity = await UserActivityRepository.get_activity_by_plan_and_type(
                db=session,
                active_user_plan_id=active_plan.id,
                activity_type=ActivityTypeEnum.STORAGE_USAGE,
            )

            # Cache the storage activity
            user_activity_tracker.store_activity(user_data.username, storage_activity)
        else:
            # Get activities from cache
            if detection_type == DetectionTypeEnum.IMAGE:
                main_activity = cached_activities.get(ActivityTypeEnum.IMAGE_USAGE)
            else:
                main_activity = cached_activities.get(ActivityTypeEnum.VIDEO_USAGE)

            storage_activity = cached_activities.get(ActivityTypeEnum.STORAGE_USAGE)

        # Validate usage limits
        if main_activity.daily_usage == main_activity.daily_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your have exceeded daily limit, Please come tomorrow or upgrade your plan."
            )

        if main_activity.total_usage == main_activity.total_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your usage_quota is full, Please upgrade your plan."
            )

        return {
            "image_activity": main_activity.model_dump(mode="json") if detection_type == DetectionTypeEnum.IMAGE else None,
            "video_activity": main_activity.model_dump(mode="json") if detection_type == DetectionTypeEnum.VIDEO else None,
            "storage_activity": storage_activity.model_dump(mode="json")
        }
    except Exception as e:
        log.error(f"Error in validate_usage_limit: {str(e)}")
        raise


@router.get(
    "/",
    response_model=DetectionWithCount,
    status_code=status.HTTP_200_OK,
    summary="Get List of Detection Data",
)
async def get_detections(
    page: int = Query(settings.DEFAULT_PAGE),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT),
    image_id: int = Query(None),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    try:
        return await DetectionService.get_detection_results(
            db=db,
            page=page,
            limit=limit,
            user_id=auth_obj["user"].id,
            image_id=image_id or None,
        )

    except Exception as e:
        log.error(f"Unexpected error in get_detections: {str(e)}")
        raise


@router.post(
    "/image", 
    response_model=DetectionResults, 
    status_code=status.HTTP_200_OK,
    summary="Perform Image Detection",
)
async def image_detection(
    file: UploadFile = File(..., description="Image or video file."),
    model_size: ModelSizeEnum = Form(ModelSizeEnum.SMALL, description="Model size."),
    requested_services: str = Form(None, description="List of requested services as a JSON string."),
    client_id: str = Form(..., description="Client ID for WebSocket communication"),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    try:
        requested_services_list = json.loads(requested_services) if requested_services else None    

        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file is missing."
            )        

        if client_id not in local_storage.active_connections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="WebSocket connection not established. Connect to /ws/{client_id} first."
            )            

        usage_data = await validate_usage_limit(
            db, auth_obj.get("user"), detection_type=DetectionTypeEnum.IMAGE
        )

        request_data = DetectionRequest(
            model_size=model_size,
            requested_services=requested_services_list,
        )

        detection_task_id = str(uuid.uuid4())

        # Notify client that processing has started
        await local_storage.active_connections[client_id].send_json({
            "type": WebSocketMessageType.STATUS,
            "status": "started",
            "task_id": detection_task_id,
            "message": "Detection process started"
        })

        result = await DetectionService.image_detection_ws(
            file=file, 
            request_data=request_data, 
            user_data=auth_obj["user"],
            websocket=local_storage.active_connections[client_id],
            task_id=detection_task_id
        )    
        update_user_activity_task.delay(
            username=auth_obj.get("user").username,
            user_activities=usage_data,
            file_size=file.size,
            service_count=len(requested_services_list) if len(requested_services_list) > 0 else 4,
        )
        return result

    except json.JSONDecodeError as json_err:
        log.error(f"JSON parsing error: {str(json_err)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid JSON format for requested_services.",
        )

    except HTTPException as http_err:
        log.error(f"Http error in image_detection: {str(http_err)}")
        raise

    except Exception as e:
        log.error(f"Unexpected error in image_detection: {str(e)}")
        raise
