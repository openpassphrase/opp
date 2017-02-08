import { Observable } from 'rxjs/Observable';
import * as item from '../actions/items';
import { IItem } from '../passwords/models';

export interface State {
  loading: boolean;
  items: IItem[];
}

const initialState: State = {
  loading: false,
  items: []
};

export function reducer(state = initialState, action: item.Actions): State {
  if (action instanceof item.LoadItemsSuccessAction) {
    return {
      loading: false,
      items: [...action.payload]
    };
  } else if (action instanceof item.AddItemAction) {
    return {
      loading: true,
      items: [...state.items, action.payload]
    };
  } else if (action instanceof item.AddItemSuccessAction) {
    return {
      loading: false,
      items: state.items.map(x => x.id === undefined && x.name === action.payload.name
        ? Object.assign({}, x, { id: action.payload.id })
        : x)
    };
  } else if (action instanceof item.AddItemFailAction) {
    return {
      loading: false,
      items: state.items.filter(x => x.name !== action.payload.name)
    };
  } else if (action instanceof item.UpdateItemAction) {
    return {
      loading: true,
      items: state.items.map(x => x.id === action.payload.newItem.id
        ? Object.assign({}, action.payload.newItem)
        : x)
    };
  } else if (action instanceof item.UpdateItemFailAction) {
    return {
      loading: false,
      items: state.items.map(x => x.id === action.payload.id
        ? Object.assign({}, action.payload)
        : x)
    };
  } else if (action instanceof item.UpdateItemSuccessAction) {
    return {
      loading: false,
      items: state.items
    };
  } else if (action instanceof item.RemoveItemAction) {
    return {
      loading: true,
      items: state.items.filter(x => x.id !== action.payload.id)
    };
  } else if (action instanceof item.RemoveItemFailAction) {
    return {
      loading: false,
      items: [...state.items, action.payload]
    };
  } else if (action instanceof item.RemoveItemsFromCategory) {
    return {
      loading: false,
      items: state.items.filter(x => x.category_id !== action.payload)
    };
  } else if (action instanceof item.SetItemsCategoryByCategoryId) {
    return {
      loading: false,
      items: state.items.map(x => x.category_id === action.payload.fromCategoryId
        ? Object.assign({}, x, { category_id: action.payload.toCategoryId })
        : x)
    };
  } else if (action instanceof item.RemoveItemSuccessAction) {
    return {
      loading: false,
      items: state.items
    };
  } else {
    return state;
  }
}

export function getItems(state$: Observable<State>) {
  return state$.select(s => s.items);
}

export function getLoading(state$: Observable<State>) {
  return state$.select(s => s.loading);
}