import { ICategory, IUpdateCategoryPayload, IRemoveCategoryPayload } from '../passwords/models';

export class SecretPhraseChangeAction {
  constructor(public payload: string) { }
}

export class LoadCategoriesAction {
  constructor() { }
}

export class LoadCategoriesSuccessAction {
  constructor(public payload: ICategory[]) { }
}

export class AddCategoryAction {
  constructor(public payload: string) { }
}

export class AddCategorySuccessAction {
  constructor(public payload: ICategory) { }
}

export class AddCategoryFailAction {
  constructor(public payload: string) { }
}

export class EditCategoryAction {
  constructor(public payload: IUpdateCategoryPayload) { }
}

export class EditCategorySuccessAction {
  constructor() { }
}

export class EditCategoryFailAction {
  constructor(public payload: IUpdateCategoryPayload) { }
}

export class RemoveCategoryAction {
  constructor(public payload: IRemoveCategoryPayload) { }
}

export class RemoveCategorySuccessAction {
  constructor() { }
}

export class RemoveCategoryFailAction {
  constructor(public payload: IRemoveCategoryPayload) { }
}

export type Actions
  = SecretPhraseChangeAction
  | LoadCategoriesAction
  | LoadCategoriesSuccessAction
  | AddCategoryAction
  | AddCategorySuccessAction
  | AddCategoryFailAction
  | EditCategoryAction
  | EditCategorySuccessAction
  | EditCategoryFailAction
  | RemoveCategoryAction
  | RemoveCategorySuccessAction
  | RemoveCategoryFailAction;
