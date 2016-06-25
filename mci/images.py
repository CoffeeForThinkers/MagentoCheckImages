import logging
import requests

import ma.api.product
import ma.api.media

import mci.config.images
import mci.progress

_LOGGER = logging.getLogger(__name__)


class Images(object):
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
