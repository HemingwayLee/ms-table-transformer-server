import os
import json
import base64
import subprocess
from pathlib import Path
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# def _remove_transparency(im, bg_colour=(255, 255, 255)):

#     # Only process if image has transparency (http://stackoverflow.com/a/1963146)
#     if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

#         # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
#         alpha = im.convert('RGBA').split()[-1]

#         # Create a new background image of our matt color.
#         # Must be RGBA because paste requires both images have the same format
#         # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
#         bg = Image.new("RGBA", im.size, bg_colour + (255,))
#         bg.paste(im, mask=alpha)
#         return bg

#     else:
#         return im

@require_http_methods(["GET"])
def list_images(request):
    files = []
    for filename in os.listdir(f"{settings.MEDIA_ROOT}/images"):
        if filename.endswith(".jpg"):
            files.append(filename)

    return JsonResponse({"images": files})


@require_http_methods(["POST"])
def predict(request):
    body = json.loads(request.body)
    print(body["filename"])
    if body["filename"] != '':
        process = subprocess.Popen([f"/home/app/backend/src/prediction.sh {body['filename']}"], shell=True, stdout=subprocess.PIPE, cwd="/home/app/backend/src/")
        process.wait()
        print(process.returncode)

        if process.returncode == 0:
            with open(f"{settings.MEDIA_ROOT}/images/{Path(body['filename']).stem}_objects.json", "r") as fp:
                res = json.load(fp)
    
            return JsonResponse({"result": "completed!", "result": res})
        else:
            return JsonResponse({"result": "error!", "code": process.returncode})
    else:
        return JsonResponse({"result": "no filename!"})


@require_http_methods(["POST"])
def upload_file(request):
    uploadedFile = request.FILES['myfile'] if 'myfile' in request.FILES else False
    if uploadedFile:
        fss = FileSystemStorage(f"{settings.MEDIA_ROOT}/images/")
        filename = fss.save(uploadedFile.name, uploadedFile)
        return JsonResponse({'result': 'uploaded'})
    else:
        return JsonResponse({'result': 'no file uploaded' }, status=400)



@require_http_methods(["POST"])
def cleanup_results(request):
    return JsonResponse({"result": "removed"})


