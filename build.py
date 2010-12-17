import logging
import os
import re
import zipfile

ZIP_SKIP_RE = re.compile('\.svn|\.pyc|\.[pm]o')
IGNORED_CONTRIB = []

def bootstrap(only_check_for_zips=False):
  logging.info('Beginning bootstrap...')
  l = os.listdir('vendor')
  for vendor_lib in l:
    if vendor_lib.startswith('.'):
      continue
    if only_check_for_zips and os.path.exists('%s.zip' % vendor_lib):
      continue
    logging.info('Building zip for %s...' % vendor_lib)
    zip_vendor_lib(vendor_lib)
  logging.info('Finishing bootstrap.')
  
def zip_vendor_lib(lib):
  f = zipfile.ZipFile('%s.zip' % lib, 'w')

  for dirpath, dirnames, filenames in os.walk('vendor/%s' % lib):
    if dirpath == os.path.join('vendor', lib, 'contrib'):
      _strip_contrib(dirnames)

    for filename in filenames:
      name = os.path.join(dirpath, filename)
      if ZIP_SKIP_RE.search(name):
        logging.debug('Skipped (skip_re): %s', name)
        continue
      if not os.path.isfile(name):
        logging.debug('Skipped (isfile): %s', name)
        continue
      logging.debug('Adding %s...', name)
      f.write(name, name[len('vendor/'):], zipfile.ZIP_DEFLATED)

  f.close()
  
def _strip_contrib(dirnames):
  for d in IGNORED_CONTRIB:
    try:
      dirnames.remove(d)
    except ValueError:
      pass