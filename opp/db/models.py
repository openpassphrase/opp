# Copyright 2017 OpenPassPhrase
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64
from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey,
                        Index, Integer, Sequence, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):

    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, Sequence('item_id_seq'), primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())


class Item(Base):

    __tablename__ = 'items'
    __table_args__ = (Index('category_id_idx', 'category_id'),
                      {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'})

    id = Column(Integer, Sequence('item_id_seq'), primary_key=True)
    category_id = Column(Integer, Sequence('category_id_seq'),
                         ForeignKey('categories.id'), default=None)
    user_id = Column(Integer, Sequence('user_id_seq'),
                     ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=True, default=None)
    url = Column(String(2000), nullable=True, default=None)
    account = Column(String(255), nullable=True, default=None)
    username = Column(String(255), nullable=True, default=None)
    password = Column(String(255), nullable=True, default=None)
    blob = Column(String(4096), nullable=True, default=None)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())

    category = relationship('Category')
    user = relationship('User')

    def extract(self, cipher, with_category=True):
        # Create a list of all encrypted columns
        row = [self.name, self.url, self.account, self.username,
               self.password, self.blob]

        # Concatenate all the columns into one big blob and decrypt
        row = cipher.decrypt("".join(row))

        # Split decrypted data by delimeter and perform base64 decode
        extracted_values = [base64.b64decode(x).decode() for
                            x in row.split('~')]

        # Create item object
        item = {'id': self.id,
                'name': extracted_values[0],
                'url': extracted_values[1],
                'account': extracted_values[2],
                'username': extracted_values[3],
                'password': extracted_values[4],
                'blob': extracted_values[5]}
        if with_category:
            if self.category:
                item['category'] = self.category.extract(cipher)
            else:
                item['category'] = {"id": self.category_id}

        return item


class Category(Base):

    __tablename__ = 'categories'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, Sequence('user_id_seq'),
                     ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())

    items = relationship('Item', order_by=Item.id)
    user = relationship('User')

    def extract(self, cipher, with_items=False):
        category = {'id': self.id,
                    'name': cipher.decrypt(self.name)}
        if with_items:
            items_array = []
            for item in self.items:
                items_array.append(item.extract(cipher, False))
            category['items'] = items_array
        return category
