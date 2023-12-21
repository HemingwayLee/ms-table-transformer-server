import os
import json
import base64
from PIL import Image, ImageOps
from io import BytesIO
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .demo import main

def _remove_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im

@require_http_methods(["GET"])
def list_images(request):
    files = []
    for filename in os.listdir(f"{settings.MEDIA_ROOT}/places2_512_object/images"):
        if filename.endswith(".png"):
            files.append(filename)

    return JsonResponse({"images": files})


@require_http_methods(["POST"])
def predict(request):
    body = json.loads(request.body)
    # print(body["filename"])
    # print(body["mask"])

    # with open(f"{settings.MEDIA_ROOT}/tmpMask.png", "wb") as fh:
    #     fh.write(base64.decodebytes(bytes(body["mask"], "utf-8")))
    
    im = Image.open(BytesIO(base64.b64decode(bytes(body["mask"], "utf-8"))))
    im = _remove_transparency(im)
    im = im.convert("RGB")
    im.save(f"{settings.MEDIA_ROOT}/tmpMask.png")

    main(
        model_name='migan-256', 
        model_path=f"{settings.MEDIA_ROOT}/models/migan_256_places2.pt", 
        img_path=f"{settings.MEDIA_ROOT}/places2_512_object/images/{body['filename']}",
        mask_path=f"{settings.MEDIA_ROOT}/tmpMask.png",
        output_path=f"{settings.MEDIA_ROOT}",
        invert=False,
    )

    # Note: Testing
    # main(
    #     model_name='migan-256', 
    #     model_path=f"{settings.MEDIA_ROOT}/models/migan_256_places2.pt", 
    #     img_path=f"{settings.MEDIA_ROOT}/places2_512_object/images/2.png",
    #     mask_path=f"{settings.MEDIA_ROOT}/places2_512_object/masks/2.png",
    #     output_path=f"{settings.MEDIA_ROOT}",
    #     invert=True,
    # )

    return JsonResponse({"result": "updated!"})


@require_http_methods(["POST"])
def cleanup_results(request):
    dir_name = f"{settings.MEDIA_ROOT}"
    for item in os.listdir(dir_name):
        if item.endswith(".png"):
            os.remove(os.path.join(dir_name, item))

    return JsonResponse({"result": "removed"})
