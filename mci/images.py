import logging
import requests
import collections
import os

import ma.api.product
import ma.api.media

import mci.constants
import mci.config.images
import mci.progress

_LOGGER = logging.getLogger(__name__)


class Images(object):
    def __init__(self):
        self.__use_path = bool(mci.config.images.MAGENTO_PATH)

    def images_gen(self, product_id):
        ma_ = ma.api.media.MediaApi()
        images = ma_.get_list_with_product_id(product_id)

        return images

    def __check_image_via_url(self, image):
        url = image['url']

        r = requests.head(url, stream=True)

        try:
            r.raise_for_status()  
        except requests.HTTPError:
            _LOGGER.warning("Not found: (%d) [%s] [%s]",
                            i, s, image['label'])

            return mci.constants.IE_DOES_NOT_EXIST
        else:
            len_ = int(r.headers['Content-Length'])
            if len_ < mci.config.images.MINIMUM_IMAGE_SIZE_B:
                _LOGGER.warning("Found but too small: (%d) [%s] [%s]",
                                i, s, image['label'])

                return mci.constants.IE_TOO_SMALL

        return None

    def __check_image_via_path(self, image):
        filepath = os.path.join(mci.config.images.MAGENTO_PATH, 'media/catalog/product' + image['file'])
        
        if os.path.exists(filepath) is False:
            return mci.constants.IE_DOES_NOT_EXIST

        s = os.stat(filepath)
        if s.st_size < mci.config.images.MINIMUM_IMAGE_SIZE_B:
            return mci.constants.IE_TOO_SMALL

        return None

    def __check_image(self, image):
        if self.__use_path is True:
            return self.__check_image_via_path(image)
        else:
            return self.__check_image_via_url(image)

    def bad_images_gen(self):
        pa = ma.api.product.ProductApi()
        ma_ = ma.api.media.MediaApi()

        _LOGGER.info("Reading products.")
        products = pa.get_list()
        products = list(products)
        product_len = len(products)

        p = mci.progress.Progress(
                product_len, 
                mci.config.images.PROGRESS_INTERVAL_S)

        for pi, product in enumerate(products):
            s = product['sku']
            i = product['product_id']

#            _LOGGER.debug("Reading images for product (%d/%d): (%d) [%s]", 
#                          pi + 1, product_len, i, s)

            images = ma_.get_list_with_product_id(i)
            image_len = len(images)

            for ii, image in enumerate(images):
                error = self.__check_image(image)
                if error == mci.constants.IE_DOES_NOT_EXIST:
                    _LOGGER.warning("Not found: (%d) [%s] [%s]", 
                                    i, s, image['label'])

                    yield (i, s, image, ())
                elif error == mci.constants.IE_TOO_SMALL:
                    _LOGGER.warning("Found but too small: (%d) [%s] [%s]",
                                    i, s, image['label'])

                    yield (i, s, image, ())

            p.tick()

    def duplicate_images_gen(self):
        pa = ma.api.product.ProductApi()
        ma_ = ma.api.media.MediaApi()

        _LOGGER.info("Reading products.")
        products = pa.get_list()
        products = list(products)
        product_len = len(products)

        p = mci.progress.Progress(
                product_len, 
                mci.config.images.PROGRESS_INTERVAL_S)

        duplicates = collections.defaultdict(list)
        for pi, product in enumerate(products):
            s = product['sku']
            i = product['product_id']

            _LOGGER.debug("Reading images for product (%d/%d): (%d) [%s]", 
                          pi + 1, product_len, i, s)

            images = ma_.get_list_with_product_id(i)
            images = \
                sorted(
                    images, 
                    key=lambda image: (
                        image['position'], 
                        image['file']))

            image_len = len(images)

            tracker = {}
            for image in images:
                try:
                    tracker[image['label']]
                except KeyError:
                    tracker[image['label']] = image
                else:
                    yield (i, s, image, (tracker[image['label']],))

            p.tick()

    def remove(self, results_gen):
        ma_ = ma.api.media.MediaApi()

        for i, s, image, _ in results_gen:
            _LOGGER.info("Removing image with file-path [%s] from product [%s].", image['file'], s)
            ma_.remove_with_sku(s, image['file'])

