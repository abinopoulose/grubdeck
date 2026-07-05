
class Theme:
    def __init__(self, data):
        self.id = data.get("id")
        self.name = data.get("name")
        self.cover_image = data.get("cover_image")
        self.description = data.get("description", "")
        self.carousel_images = data.get("carousel_images", [])
        self.size_options = data.get("size_options", [])
        self.created_by = data.get("created_by", {})
