import logging

from blob.models import Blob

class BlobHelper(object):
  @staticmethod
  def save_with_thumbails(request, form, picture, username, sizes):
    logging.info("****** blob.helpers.BlobHelper.save_thumbails")
    if form.is_valid():
      item = form.save()
      if picture is not None:
        reader = picture.open()
        thumbails = Blob.create_thumbails(form.cleaned_data['slug'],
                                          reader.read(),
                                          picture.content_type,
                                          username=username,
                                          sizes=sizes)
        item.pictures = thumbails
        item.picture_blob = picture
        item.save()

      return item
    else:
      request.session['form_data'] = request.POST
      if picture is not None:
        picture.delete()

    return None 