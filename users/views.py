import logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_photo(request):
    logger.info('Starting photo upload process')
    logger.info(f'Request user: {request.user}')
    logger.info(f'Request FILES: {request.FILES}')
    
    if 'photo' not in request.FILES:
        logger.error('No photo file in request')
        return Response({'error': 'No photo file provided'}, status=400)
    
    photo = request.FILES['photo']
    logger.info(f'Photo details - name: {photo.name}, size: {photo.size}, content_type: {photo.content_type}')
    
    try:
        # Save the photo
        user = request.user
        user.photo = photo
        user.save()
        
        logger.info(f'Photo saved successfully. New photo path: {user.photo.path}')
        logger.info(f'Photo URL: {user.photo.url}')
        
        return Response({
            'message': 'Photo uploaded successfully',
            'photo': user.photo.url
        })
    except Exception as e:
        logger.error(f'Error saving photo: {str(e)}', exc_info=True)
        return Response({'error': str(e)}, status=500) 