import '@ngrx/core/add/operator/select';
import { Observable } from 'rxjs/Observable';
import { ICategory } from '../passwords/models';
import * as category from '../actions/categories';

export interface State {
  loading: boolean;
  categories: ICategory[];
}

const initialState: State = {
  loading: false,
  categories: [],
};

export function reducer(state = initialState, action: category.Actions): State {
  if (action instanceof category.LoadCategoriesAction) {
    return {
      loading: true,
      categories: []
    };
  } else if (action instanceof category.LoadCategoriesSuccessAction) {
    return {
      loading: false,
      categories: [...action.payload]
    };
  } else if (action instanceof category.AddCategoryAction) {
    return {
      loading: true,
      categories: [...state.categories, { id: undefined, name: action.payload }]
    };
  } else if (action instanceof category.AddCategoryFailAction) {
    return {
      loading: false,
      categories: state.categories.filter(c => c.id !== undefined && c.name !== action.payload)
    };
  } else if (action instanceof category.AddCategorySuccessAction) {
    return {
      loading: false,
      categories: state.categories.map(c => {
        return c.id === undefined && c.name === action.payload.name
          ? Object.assign({}, c, { id: action.payload.id })
          : c;
      })
    };
  } else if (action instanceof category.EditCategoryAction) {
    return {
      loading: true,
      categories: state.categories.map(c => {
        return c.id === action.payload.id
          ? Object.assign({}, c, { name: action.payload.name })
          : c;
      })
    };
  } else if (action instanceof category.EditCategorySuccessAction) {
    return {
      loading: false,
      categories: state.categories
    };
  } else if (action instanceof category.EditCategoryFailAction) {
    return {
      loading: false,
      categories: state.categories.map(c => {
        return c.id === action.payload.id
          ? Object.assign({}, c, { name: action.payload.initialName })
          : c;
      })
    };
  } else if (action instanceof category.RemoveCategoryAction) {
    return {
      loading: true,
      categories: state.categories.filter(c => c.id !== action.payload.category.id)
    };
  } else if (action instanceof category.RemoveCategoryFailAction) {
    return {
      loading: false,
      categories: [...state.categories, action.payload.category]
    };
  } else if (action instanceof category.RemoveCategorySuccessAction) {
    return {
      loading: false,
      categories: state.categories
    };
  } else {
    return state;
  }
}

export function getCategories(state$: Observable<State>) {
  return state$.select(s => s.categories);
}

export function getLoading(state$: Observable<State>) {
  return state$.select(s => s.loading);
}