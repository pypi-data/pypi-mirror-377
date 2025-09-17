# Copyright (C) 2022-2025 Indoc Systems
#
# Contact Indoc Systems for any questions regarding the use of this source code.

import time
import uuid


class GenerateId:
    def generate_id(self):
        return str(uuid.uuid4())

    def time_hash(self):
        return str(time.time())[0:10]
