export interface ICategory {
  id: number;
  name: string;
}

export interface IItem {
  id: number;
  name?: string;
  url?: string;
  account?: string;
  password?: string;
  blob?: string;
  category_id?: number;
}

export interface ICategoryItems extends ICategory {
  items: IItem[];
}

export interface IUpdateCategoryPayload extends ICategory {
  initialName: string;
}

export interface IRemoveCategoryPayload {
  category: ICategory;
  cascade: boolean;
}

export interface IUpdateItemPayload {
  newItem: IItem;
  initialItem: IItem;
}
