import logging
import requests
import collections

import ma.api.product
import ma.api.media

import mci.config.images
import mci.progress

_LOGGER = logging.getLogger(__name__)


class Images(object):
    def images_gen(self, product_id):
        ma_ = ma.api.media.MediaApi()
        images = ma_.get_list_with_product_id(i)

        return images

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

            _LOGGER.debug("Reading images for product (%d/%d): (%d) [%s]", 
                          pi + 1, product_len, i, s)

            images = ma_.get_list_with_product_id(i)
            image_len = len(images)

            for ii, image in enumerate(images):
                url = image['url']

                _LOGGER.debug("Checking image (%d/%d) for (%d) [%s]: [%s]", 
                              ii + 1, image_len, i, s, url)

                r = requests.head(url, stream=True)

                try:
                    r.raise_for_status()
                except requests.HttpError:
                    _LOGGER.warning("Not found: (%d) [%s] [%s]", 
                                    i, s, image['label'])

                    yield (s, i, image)

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
                    yield (i, s, image, tracker[image['label']])

            p.tick()

    def remove_duplicates(self, duplicates_gen):
        ma_ = ma.api.media.MediaApi()

        first_sku = None
        for i, s, image, kept in duplicates_gen:
            if first_sku is not None and s != first_sku:
                break

            _LOGGER.info("Removing duplicate image with file-path [%s] from product [%s].", image['file'], s)
            ma_.remove_with_sku(s, image['file'])

            first_sku = s
