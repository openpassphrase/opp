export interface ICategory {
  id: number;
  name: string;
  items: IItem[];
}

export interface IItem {
  id: number;
  name: string;
  url: string;
  account: string;
  password: string;
  blob: string;
}
