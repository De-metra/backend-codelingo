import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from cloudinary import CloudinaryImage

from app.core.config import settings


# Configuration       
cloudinary.config( 
    cloud_name = settings.CLOUDINARY_CLOUD_NAME, 
    api_key = settings.CLOUDINARY_API_KEY, 
    api_secret = settings.CLOUDINARY_API_SECRET, 
    secure=True
)

def upload_image(file, user_id):
    upload_result = cloudinary.uploader.upload(
        file=file,
        folder="avatars",
        public_id=str(user_id),
        overwrite=True
    )

    return upload_result["secure_url"]