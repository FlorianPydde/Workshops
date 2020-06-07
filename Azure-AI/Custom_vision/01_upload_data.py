from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry
from msrest.authentication import ApiKeyCredentials
import glob 

ENDPOINT = "https://westus2.api.cognitive.microsoft.com/"

# Replace with a valid key
training_key = "cb99d4e459a84ee4a7560c4eca6c47ac"
prediction_key = "<your prediction key>"
prediction_resource_id = "<your prediction resource id>"

publish_iteration_name = "classifyModel"

credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

# Get project
project_id = '20725ff7-16ea-4c53-bb7b-548180c7f5ce'
project = trainer.get_project(project_id)

try:
    infected_tag = trainer.create_tag(project.id, "infected")
    uninfected_tag = trainer.create_tag(project.id, "uninfected")
except Exception:
    list_tags = trainer.get_tags(project_id)
    infected_tag = [x for x in list_tags if x.name == 'infected'][0]
    uninfected_tag = [x for x in list_tags if x.name == 'uninfected'][0]


print("Adding images...")

image_list_infected = list(glob.glob('./Datasets/cell_images/train/infected/*.png'))
image_list_infected += list(glob.glob('./Datasets/cell_images/val/infected/*.png'))

image_list_uninfected = list(glob.glob('./Datasets/cell_images/train/uninfected/*.png'))
image_list_uninfected += list(glob.glob('./Datasets/cell_images/val/uninfected/*.png'))
image_list = []
print(len(image_list_infected))
print(len(image_list_uninfected))

for image_path in image_list_infected:
    file_name = "infected_{}".format(image_path.split('\\')[-1])
    with open(image_path, "rb") as image_contents:
        image_list.append(ImageFileCreateEntry(name=file_name, contents=image_contents.read(), tag_ids=[infected_tag.id]))

for image_path in image_list_uninfected:
    file_name = "uninfected_{}".format(image_path.split('\\')[-1])
    with open(image_path, "rb") as image_contents:
        image_list.append(ImageFileCreateEntry(name=file_name, contents=image_contents.read(), tag_ids=[uninfected_tag.id]))

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

list_chunk = list(chunks(image_list, 63))
upload_result = None
for i,chunk in enumerate(list_chunk):
    print(i,'/',len(list_chunk))
    upload_result = trainer.create_images_from_files(project.id, images=chunk)

if not upload_result.is_batch_successful:
    print("Image batch upload failed.")
    for image in upload_result.images:
        print("Image status: ", image.status)
    exit(-1)