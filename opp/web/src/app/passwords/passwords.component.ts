import 'rxjs/add/operator/let';
import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Store } from '@ngrx/store';
import * as fromRoot from '../reducers';
import * as category from '../actions/categories';
import * as item from '../actions/items';
import {
  ICategory, IItem, ICategoryItems, IUpdateCategoryPayload,
  IRemoveCategoryPayload, IUpdateItemPayload
} from './models';


@Component({
  selector: 'app-passwords',
  templateUrl: './passwords.component.html',
  styleUrls: ['./passwords.component.scss']
})
export class PasswordsComponent implements OnInit {
  categories$: Observable<ICategoryItems[]>;
  loading$: Observable<boolean>;
  itemsWithoutCategory$: Observable<IItem[]>;
  expanded$ = new BehaviorSubject<number[]>([]);
  private _expanded: number[] = [];

  constructor(public store: Store<fromRoot.State>) { }

  ngOnInit() {
    this.categories$ = this.store.let(fromRoot.getCategoryItems);
    this.itemsWithoutCategory$ = this.store.let(fromRoot.getItemsWithoutCategory);
    this.loading$ = this.store.let(fromRoot.getLoading);
  }

  addCategory(name: string) {
    this.store.dispatch(new category.AddCategoryAction(name) as any);
  }

  removeCategory(info: IRemoveCategoryPayload) {
    if (info.cascade) {
      this.store.dispatch(new item.RemoveItemsFromCategory(info.category.id) as any);
    } else {
      this.store.dispatch(new item.SetItemsCategoryByCategoryId({
        fromCategoryId: info.category.id,
        toCategoryId: undefined
      }) as any);
    }
    this.store.dispatch(new category.RemoveCategoryAction(info) as any);
    this.toggleCategoryExpanded(info.category.id);
  }

  updateCategory(info: IUpdateCategoryPayload) {
    this.store.dispatch(new category.EditCategoryAction(info) as any);
  }

  addItem(itemModel: IItem) {
    this.store.dispatch(new item.AddItemAction(itemModel) as any);
  }

  updateItem(info: IUpdateItemPayload) {
    this.store.dispatch(new item.UpdateItemAction(info) as any);
  }

  removeItem(i: IItem) {
    this.store.dispatch(new item.RemoveItemAction(i) as any);
  }

  toggleCategoryExpanded(id: number) {
    this._expanded = this._expanded.indexOf(id) > -1
      ? this._expanded.filter(x => x !== id)
      : [...this._expanded, id];
    this.expanded$.next(this._expanded);
  }
}
