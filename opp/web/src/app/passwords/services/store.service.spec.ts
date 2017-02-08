/* tslint:disable:no-unused-variable */
/*
import { TestBed, async, inject } from '@angular/core/testing';
import { MaterialModule, MdSnackBar, MdSnackBarModule } from '@angular/material';
import { Observable } from 'rxjs/Observable';
import { StoreService } from './store.service';
import { BackendService, IBackendService } from './backend.service';
import { ICategory, IItem } from '../models';

class BackendServiceMock implements IBackendService {
  lastCategoryId = 0;
  lastItemId = 0;

  fetchAll(): Observable<ICategory[]> {
    const categories: ICategory[] = [];
    return Observable.of(categories);
  }

  addCategory(name: string): Observable<ICategory> {
    this.lastCategoryId++;
    const category: ICategory = { name: name, id: this.lastCategoryId };
    return Observable.of(category);
  }

  updateCategory(category: ICategory): Observable<any> {
    return Observable.of({});
  }

  removeCategory(opts: { id: number, cascade: boolean }): Observable<any> {
    return Observable.of({});
  }

  addItem(item: IItem): Observable<IItem> {
    this.lastItemId++;
    item.id = this.lastItemId;
    return Observable.of(item);
  }

  updateItem(item: IItem): Observable<any> {
    return Observable.of({});
  }

  removeItem(id: number): Observable<any> {
    return Observable.of({});
  }
}

fdescribe('StoreService', () => {
  let srv: StoreService;

  beforeEach(() => {
    srv = new StoreService(new BackendServiceMock() as any, {} as any);
  });

  it('should initialize with empty categories', () => {
    expect(srv.categories).toEqual([]);
  });

  it('addCategory()', () => {
    const expectedName = 'test name';
    srv.addCategory(expectedName);
    expect(srv.categories.length).toBe(1);
    expect(srv.categories[0].id).toBe(1);
    expect(srv.categories[0].name).toBe(expectedName);
    expect(srv.categories[0].items).toEqual([]);
  });

  it('updateCategory()', () => {
    srv.addCategory('test name');
    const expectedName = 'test update';
    srv.updateCategory({ id: 1, name: expectedName });
    expect(srv.categories[0].name).toBe(expectedName);
  });

  it('removeCategory()', () => {
    srv.addCategory('test name');
    srv.removeCategory({ id: 1, cascade: true });
    expect(srv.categories).toEqual([]);
  });

  it('addItem()', () => {
    srv.addCategory('test name');
    const item: IItem = { name: 'test item', category_id: 1 } as any;
    srv.addItem(item);
    expect(srv.categories[0].items.length).toBe(1);
    expect(srv.categories[0].items[0]).toEqual({ id: 1, name: 'test item', category_id: 1 });
  });

  it('removeCategory() - cascade: true', () => {
    srv.addCategory('test name');
    const item: IItem = { name: 'test item', category_id: 1 } as any;
    srv.addItem(item);
    srv.removeCategory({ id: 1, cascade: true });
    expect(srv.categories).toEqual([]);
  });

  it('removeCategory() - cascade: false', () => {
    srv.addCategory('test name');
    const item: IItem = { name: 'test item', category_id: 1 } as any;
    srv.addItem(item);
    srv.removeCategory({ id: 1, cascade: false });
    expect(srv.categories.length).toBe(1);
    expect(srv.categories[0].id).toBe(null);
    expect(srv.categories[0].name).toBe('default');
    expect(srv.categories[0].items[0]).toEqual({ id: 1, name: 'test item', category_id: 1 });
  });

  it('updateItem', () => {
    srv.addCategory('test name');
    const item: IItem = { name: 'test item', category_id: 1 } as any;
    srv.addItem(item);
    srv.updateItem({ id: 1, name: 'new test item', category_id: 1, password: 'password' } as any);
    expect(srv.categories[0].items[0]).toEqual({ id: 1, name: 'new test item', category_id: 1, password: 'password' });
  });

  it('removeItem()', () => {
    srv.addCategory('test name');
    const item: IItem = { name: 'test item', category_id: 1 } as any;
    srv.addItem(item);
    srv.removeItem({ id: 1, category_id: 1 });
    expect(srv.categories[0].items.length).toBe(0);
  });
});
*/