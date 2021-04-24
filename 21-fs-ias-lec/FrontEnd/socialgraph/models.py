from django.db import models

# Create your models here.


class Nodes(models.Model):

    def create(self):
        nodes = [
            {
                "id": 1,
                "name": "A",
                "gender": "male"
            },
            {
                "id": 2,
                "name": "B",
                "gender": "female"
            },
            {
                "id": 3,
                "name": "C",
                "gender": "male"
            },
            {
                "id": 4,
                "name": "D",
                "gender": "male"
            },
            {
                "id": 5,
                "name": "E",
                "gender": "male"
            },
            {
                "id": 6,
                "name": "F",
                "gender": "female"
            },
            {
                "id": 7,
                "name": "G",
                "gender": "female"
            },
            {
                "id": 8,
                "name": "H",
                "gender": "male"
            },
            {
                "id": 9,
                "name": "I",
                "gender": "female"
            },
            {
                "id": 10,
                "name": "J",
                "gender": "male"
            },
            {
                "id": 11,
                "name": "K",
                "gender": "male"
            },
            {
                "id": 12,
                "name": "L",
                "gender": "female"
            },
            {
                "id": 13,
                "name": "M",
                "gender": "male"
            },
            {
                "id": 14,
                "name": "N",
                "gender": "female"
            },
            {
                "id": 15,
                "name": "O",
                "gender": "female"
            },
            {
                "id": 16,
                "name": "P",
                "gender": "female"
            }
        ]
        return nodes