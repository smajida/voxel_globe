from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
from django.core.urlresolvers import reverse

class IngestTestCase(VoxelGlobeTestCase):
  def setUp(self):
    self.client = self.setupVoxelGlobeTestCase()

    # post request to create a new upload session, which we'll upload images to
    response = self.client.post('/apps/ingest/rest/uploadsession/', {  
      'name': 'capitol', 
      'metadata_type': 'krt',
      'payload_type': 'images'
    })

    import json
    response_json = json.loads(response.content)
    self.image_session_id = response_json['id']

    response = self.client.post('/apps/ingest/rest/uploadsession/', {  
      'name': 'controlpoints',
      'metadata_type': None,
      'payload_type': None,
      'upload_types': json.dumps({'controlpoint_type': 'csv'})
    })

    response_json = json.loads(response.content)
    self.controlpoint_session_id = response_json['id']

  def test_ingest_choose_session_template(self):
    response = self.client.get('/apps/ingest/')
    self.assertEqual(response.status_code, 200)
    self.assertTrue('Start New Upload' in response.content)
    self.assertTrue('<h2>Upload</h2>' in response.content)
    templates = []
    for t in response.templates:
      templates.append(t.name)
    self.assertTrue('main/base.html' in templates)
    self.assertTrue('ingest/html/chooseSession.html' in templates)

  def test_ingest_add_image_template(self):
    response = self.client.get('/apps/ingest/addFiles?upload=' + str(self.image_session_id))
    self.assertEqual(response.status_code, 200)
    self.assertTrue('<h1>Add <span class="uploadType">image</span> files for <em>capitol</em></h1>' in response.content)
    self.assertTrue('<h2>Add Files</h2>' in response.content)
    templates = []
    for t in response.templates:
      templates.append(t.name)
    self.assertTrue('main/base.html' in templates)
    self.assertTrue('ingest/html/addFiles.html' in templates)

  def test_image_ingest(self):
    import urllib2, ssl, os, zipfile, shutil

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib2.urlopen('https://vsi-ri.com/data/pvd_2006_capitol_images_and_cameras.zip', context=ctx)
    
    dir_url = os.path.join(os.getenv('VIP_TEMP_DIR'), 'test_images')
    if not os.path.exists(dir_url):
      os.mkdir(dir_url)
    zip_url = os.path.join(dir_url, 'zipfile')
    
    with open(zip_url, 'w+') as z:
      z.write(response.read())

    zip_ref = zipfile.ZipFile(zip_url, 'r')
    zip_ref.extractall(dir_url)
    zip_ref.close()

    os.remove(zip_url)

    response = self.client.get('/apps/ingest/addFiles?upload=' + str(self.image_session_id))
    testFile = response.context['testFile']

    image_count = 0;

    os.chdir(dir_url)

    for dirpath, subdirs, files in os.walk(os.getcwd()):
      for f in files:
        with open(f) as fp:
          if f.endswith('.png'):
            image_count += 1
          if f.endswith('.csv'):
            continue
          response = self.client.post('/apps/ingest/uploadImage', {
            'name': 'filedrop',
            'filename': f,
            'file': fp,
            'uploadSession': self.image_session_id,
            'testFile': testFile
          })

    response = self.client.post('/apps/ingest/ingestFolderImage', {
      'uploadSession': self.image_session_id
    })

    shutil.rmtree(dir_url)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(models.CameraSet.objects.all()), 1)
    self.assertEqual(len(models.ImageSet.objects.all()), 1)
    self.assertEqual(len(models.Camera.objects.all()), image_count)
    self.assertEqual(len(models.Image.objects.all()), image_count)
    self.assertEqual(len(models.Scene.objects.all()), 1)
    self.assertEqual(len(models.GeoreferenceCoordinateSystem.objects.all()), image_count)
    self.assertEqual(len(models.CoordinateTransform.objects.all()), image_count)
    self.assertEqual(len(models.CoordinateSystem.objects.all()), image_count * 2)
    self.assertEqual(len(models.CartesianTransform.objects.all()), image_count)
    self.assertEqual(len(models.CartesianCoordinateSystem.objects.all()), image_count)
    self.assertTrue(models.ImageSet.objects.all()[0].name.startswith('capitol'))


  # def test_controlpoint_ingest(self):
  #   response = self.client.get('/apps/ingest/addFiles?upload=' + str(self.controlpoint_session_id))
  #   self.assertEqual(response.status_code, 200)
  #   testFile = response.context['testFile']

  #   import os
  #   os.chdir('  TODO   ')
  #   f = 'apartment.csv'
  #   with open(f) as fp:
  #     response = self.client.post('/apps/ingest/uploadControlpoint', {
  #       'name': 'filedrop',
  #       'filename': f,
  #       'file': fp,
  #       'uploadSession': self.controlpoint_session_id,
  #       'testFile': testFile
  #     })
  #     self.assertEqual(response.status_code, 200)

  #   response = self.client.post('/apps/ingest/ingestFolderControlpoint', {
  #     'uploadSession': str(self.controlpoint_session_id)
  #   })

  #   self.assertEqual(response.status_code, 200)
  #   self.assertEqual(len(models.ControlPoint.objects.all()), 116)

  def tearDown(self):
    self.tearDownVoxelGlobeTestCase()