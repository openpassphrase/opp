import { Injectable } from '@angular/core';
import { Headers } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { AuthHttp } from 'angular2-jwt';
import { ICategory, IItem } from '../models';
import { environment } from '../../../environments/environment';

export interface IBackendService {
  fetchAll(): Observable<{ categories: ICategory[], items: IItem[] }>;
  addCategory(name: string): Observable<ICategory>;
  updateCategory(category: ICategory): Observable<any>;
  removeCategory(opts: { id: number, cascade: boolean }): Observable<any>;
  addItem(item: IItem): Observable<IItem>;
  updateItem(item: IItem): Observable<any>;
  removeItem(id: number): Observable<any>;
}

const baseUrl = `${window.location.protocol}//${window.location.hostname}${environment.baseHref}`;

@Injectable()
export class BackendService implements IBackendService {
  private headers: Headers;

  constructor(private http: AuthHttp) { }

  secretPassphraseChange(secret: string) {
    if (!this.headers) {
      this.headers = new Headers();
    }
    this.headers.set('x-opp-phrase', secret);
  }

  fetchAll(): Observable<{ categories: ICategory[], items: IItem[] }> {
    return this.http.get(`${baseUrl}/api/v1/fetchall`, { headers: this.headers })
      .map(res => res.json());
  }

  getCategories(): Observable<ICategory[]> {
    return this.http.get(`${baseUrl}/api/v1/categories`, { headers: this.headers })
      .map(res => res.json())
      .map(x => x.categories);
  }

  addCategory(name: string): Observable<ICategory> {
    return this.http.put(`${baseUrl}/api/v1/categories`,
      { category_names: [name] },
      { headers: this.headers }
    ).map(res => res.json())
      .map(x => x.categories[0]);
  }

  updateCategory(category: ICategory): Observable<void> {
    return this.http.post(`${baseUrl}/api/v1/categories`,
      { categories: [category] },
      { headers: this.headers }
    ).map(res => res.json());
  }

  removeCategory(opts: { id: number, cascade: boolean }): Observable<void> {
    return this.http.delete(`${baseUrl}/api/v1/categories`, {
      body: {
        cascade: opts.cascade,
        ids: [opts.id]
      },
      headers: this.headers
    }).map(res => res.json());
  }

  getItems(): Observable<IItem[]> {
    return this.http.get(`${baseUrl}/api/v1/items`, { headers: this.headers })
      .map(res => res.json())
      .map(x => x.items);
  }

  addItem(item: IItem): Observable<IItem> {
    return this.http.put(`${baseUrl}/api/v1/items`, { items: [item] }, { headers: this.headers })
      .map(res => res.json())
      .map(x => x.items[0]);
  }

  updateItem(item: IItem): Observable<void> {
    return this.http.post(`${baseUrl}/api/v1/items`, { items: [item] }, { headers: this.headers })
      .map(res => res.json());
  }

  removeItem(id: number): Observable<void> {
    return this.http.delete(`${baseUrl}/api/v1/items`, {
      body: { ids: [id] },
      headers: this.headers
    }).map(res => res.json());
  }
}
