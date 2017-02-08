import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/switchMap';
import 'rxjs/add/observable/from';

import { Injectable } from '@angular/core';
import { Effect, Actions } from '@ngrx/effects';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { combineLatest } from 'rxjs/observable/combineLatest';

import { BackendService } from '../passwords/services/backend.service';
import * as item from '../actions/items';
import { ICategory } from '../passwords/models';

@Injectable()
export class ItemEffects {

  @Effect()
  addItem$: Observable<any> = this.action$
    .filter(a => a instanceof item.AddItemAction)
    .switchMap((a) => this.backend.addItem(a.payload)
      .map(resp => new item.AddItemSuccessAction(resp))
      .catch(er => of(new item.AddItemFailAction(a.payload)))
    );

  @Effect()
  updateItem$: Observable<any> = this.action$
    .filter(a => a instanceof item.UpdateItemAction)
    .switchMap((a) => this.backend.updateItem(a.payload.newItem)
      .map(resp => new item.UpdateItemSuccessAction())
      .catch(er => of(new item.UpdateItemFailAction(a.payload.initialItem)))
    );

  @Effect()
  removeItem$: Observable<any> = this.action$
    .filter(a => a instanceof item.RemoveItemAction)
    .switchMap((a) => this.backend.removeItem(a.payload.id)
      .map(resp => new item.RemoveItemSuccessAction())
      .catch(er => of(new item.RemoveItemFailAction(a.payload)))
    );

  constructor(private action$: Actions, private backend: BackendService) { }
}
