/*import { Injectable } from '@angular/core';
import { MdSnackBar } from '@angular/material';
import { BackendService } from './backend.service';
import { ICategory, IItem } from '../models';

@Injectable()
export class StoreService {
  categories: ICategory[] = [];

  constructor(private backend: BackendService, private snackBar: MdSnackBar) {}

  fetchAll() {
    this.backend.fetchAll().subscribe(
      (data) => { this.categories = data; },
      (error) => console.log(error)
    );
  }

  addCategory(name: string) {
    this.backend.addCategory(name).subscribe(
      (newCategory: ICategory) => {
        if (!newCategory.items) {
          newCategory.items = [];
        }
        this.categories = [...this.categories, newCategory];
      },
      (error) => {
        console.log(error);
        this.snackBar.open('Could not add category', undefined, { duration: 6000 });
      }
    );
  }

  updateCategory(category: ICategory) {
    this.backend.updateCategory(category).subscribe(
      () => {
        this.categories = this.categories.map(c => {
          return c.id === category.id
            ? Object.assign({}, c, { name: category.name })
            : c;
        });
      },
      (error) => {
        console.log(error);
        this.snackBar.open('Could not add category', undefined, { duration: 6000 });
      }
    );
  }

  removeCategory(opts: { id: number, cascade: boolean }) {
    this.backend.removeCategory(opts).subscribe(
      () => {
        const ix = this.categories.findIndex(x => x.id === opts.id);

        const defaultIx = this.categories.findIndex(c => c.id === null);

        if (!opts.cascade) {
          const itemsToMove = this.categories[ix].items;

          if (defaultIx > -1) {
            this.categories = this.categories.map(c => {
              return c.id === null
                ? Object.assign({}, c, { items: [...c.items, ...itemsToMove] })
                : c;
            });
          } else {
            const defaultCategory: ICategory = {
              id: null,
              name: 'default',
              items: itemsToMove
            } as any;
            this.categories = [...this.categories, defaultCategory];
          }
        }

        this.categories = this.categories.filter(c => c.id !== opts.id);
      },
      (error) => {
        console.log(error);
        this.snackBar.open('Could not delete category', undefined, { duration: 6000 });
      }
    );
  }

  addItem(item: IItem) {
    this.backend.addItem(item).subscribe(
      (newItem) => {
        this.categories = this.categories.map(c => {
          return c.id === item.category_id
            ? Object.assign({}, c, { items: [...c.items, newItem] })
            : c;
        });
      },
      (error) => {
        console.log(error);
        this.snackBar.open('Could not add item', undefined, { duration: 6000 });
      }
    );
  }

  updateItem(item: IItem) {
    this.backend.updateItem(item).subscribe(
      () => {
        this.categories = this.categories.map(c => {
          return c.id === item.category_id
            ? Object.assign({}, c, {
              items: c.items.map(i => {
                return i.id === item.id
                  ? Object.assign({}, i, item)
                  : i;
              })
            })
            : c;
        });
      },
      (error) => {
        console.log(error);
        this.snackBar.open('Could not update item', undefined, { duration: 6000 });
      }
    );
  }

  removeItem(item: { id: number, category_id: number }) {
    this.backend.removeItem(item.id).subscribe(
      () => {
        this.categories = this.categories.map(c => {
          return c.id === item.category_id
            ? Object.assign({}, c, { items: c.items.filter(i => i.id !== item.id) })
            : c;
        });
      },
      (error) => {
        console.log(error);
        this.snackBar.open('Could not delete item', undefined, { duration: 6000 });
      }
    );
  }
}
*/