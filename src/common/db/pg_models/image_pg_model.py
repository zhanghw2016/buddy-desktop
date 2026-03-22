import db.constants as dbconst

class ImagePGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_desktop_images(self, desktop_image=None, image_type=None, zone_id=None, ui_type=None, session_type=None):
        
        conditions = {}

        if desktop_image is not None:
            conditions["desktop_image_id"] = desktop_image
        if image_type is not None:
            conditions["image_type"] = image_type
        
        if zone_id:
            conditions["zone"] = zone_id
        
        if ui_type:
            conditions["ui_type"] = ui_type
        
        if session_type:
            conditions["session_type"] = session_type
        
        image_set = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, conditions)
        if image_set is None or len(image_set) == 0:
            return None

        images = {}
        for image in image_set:
            desktop_image_id = image["desktop_image_id"]
            images[desktop_image_id] = image
            
        return images

    def get_default_image(self, zone, image_ids=None):

        conditions = dict(zone=zone, is_default=1)
        if image_ids:
            conditions["desktop_image_id"] = image_ids
        
        image_set = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, conditions)
        if image_set is None or len(image_set) == 0:
            return None

        images = {}
        for image in image_set:
            desktop_image_id = image["desktop_image_id"]
            images[desktop_image_id] = image
            
        return images

    def get_system_image(self, image_ids, zone_id=None):

        conditions = dict(image_id=image_ids)
        if zone_id:
            conditions["zone"] = zone_id

        image_set = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, conditions)
        if image_set is None or len(image_set) == 0:
            return None

        images = {}
        for image in image_set:
            desktop_image_id = image["desktop_image_id"]
            images[desktop_image_id] = image
            
        return images
    
    def get_desktop_resource_image(self, desktop_ids):

        conditions = dict(desktop_id=desktop_ids)

        desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)
        if desktop_set is None or len(desktop_set) == 0:
            return None

        desktop_image = {}
        for desktop in desktop_set:
            desktop_id = desktop["desktop_id"]
            desktop_image_id = desktop["desktop_image_id"]
            desktop_image[desktop_id] = desktop_image_id
        
        conditions = dict(desktop_image_id=desktop_image.values())
        image_set = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, conditions)
        if image_set is None or len(image_set) == 0:
            return None

        images = {}
        for image in image_set:
            desktop_image_id = image["desktop_image_id"]
            image_id = image["image_id"]
            images[desktop_image_id] = image_id
        
        res_image = {}
        for desktop_id, desktop_image_id in desktop_image.items():
            image_id = images[desktop_image_id]
            res_image[desktop_id] = image_id
        
        return res_image

    def get_desktop_image_info(self, desktop):

        desktop_image_id = desktop["desktop_image_id"]
        
        conditions = dict(desktop_image_id=desktop_image_id)
        image_set = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, conditions)
        if image_set is None or len(image_set) == 0:
            return None
        
        return image_set[0]

    def get_desktop_image(self, desktop_image_id):
        
        conditions = {}
        conditions["desktop_image_id"] = desktop_image_id

        image_set = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, conditions)
        if image_set is None or len(image_set) == 0:
            return None
        
        return image_set[0]
    
    def get_base_image(self, image_id):
    
        conditions = {}
        conditions["image_id"] = image_id

        image_set = self.pg.base_get(dbconst.TB_DESKTOP_IMAGE, conditions)
        if image_set is None or len(image_set) == 0:
            return None
        
        return image_set[0]
        
