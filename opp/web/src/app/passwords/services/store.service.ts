import { Injectable } from '@angular/core';
import { MdSnackBar } from '@angular/material';
import { BackendService } from './backend.service';
import { ICategory, IItem } from '../models/category';

@Injectable()
export class StoreService {
  categories: ICategory[];

  constructor(private backend: BackendService, private snackBar: MdSnackBar) {
    this.backend.fetchAll().subscribe(
      (data) => { this.categories = data; },
      (error) => console.log(error)
    );
  }

  addCategory(name: string) {
    this.backend.addCategory(name).subscribe(
      (newCategory: ICategory) => {
        this.categories.push(newCategory);
      },
      (error) => {
        console.log(error);
        this.snackBar.open('Could not add category', undefined, { duration: 6000 });
      }
    );
  }

  updateCategory(category: ICategory) {

  }

  removeCategory(id: number) {

  }
}
