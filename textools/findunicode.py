# Copyright 2019 by Sergio Valqui. All rights reserved.
with open(file) as handle:
    for b in handle.read(1):
        try:
            char = b.encode("ascii")

