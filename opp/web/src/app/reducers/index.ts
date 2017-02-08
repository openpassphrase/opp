import '@ngrx/core/add/operator/select';
import 'rxjs/add/operator/switchMap';
import 'rxjs/add/operator/let';
import { Observable } from 'rxjs/Observable';
import { combineLatest } from 'rxjs/observable/combineLatest';
import { ActionReducer, combineReducers } from '@ngrx/store';
import { compose } from '@ngrx/core/compose';

import * as fromCategories from './categories';
import * as fromItems from './items';
import { ICategoryItems } from '../passwords/models';

export interface State {
  categories: fromCategories.State;
  items: fromItems.State;
}

const reducers = {
  categories: fromCategories.reducer,
  items: fromItems.reducer
};

export function reducer(state: any, action: any) {
  return combineReducers(reducers)(state, action);
};

export const getCategoriesState = (state$: Observable<State>) =>
  state$.select(s => s.categories);

export const getItemsState = (state$: Observable<State>) =>
  state$.select(s => s.items);

export const getCategories = compose(
  fromCategories.getCategories, getCategoriesState);

export const getItems = compose(
  fromItems.getItems, getItemsState);

export const getCategoryItems = function (state$: Observable<State>) {
  return combineLatest(
    state$.let(getCategories),
    state$.let(getItems)
  )
    .map(([categories, items]) => categories.map<ICategoryItems>(c => {
      return {
        id: c.id,
        name: c.name,
        items: items.filter(x => x.category_id === c.id)
      };
    }));
};

export const getItemsWithoutCategory = function (state$: Observable<State>) {
  return state$.let(getItems)
    .map(x => x.filter(i => i.category_id === undefined || i.category_id === null));
};

export const getCategoriesLoading = compose(
  fromCategories.getLoading, getCategoriesState
);

export const getItemsLoading = compose(
  fromItems.getLoading, getItemsState
);

export const getLoading = function (state$: Observable<State>) {
  return combineLatest(
    state$.let(getCategoriesLoading),
    state$.let(getItemsLoading)
  )
    .map(([c, i]) => c && i);
};
