/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { StoreService } from './store.service';

describe('StoreService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [StoreService]
    });
  });

  it('should ...', inject([StoreService], (service: StoreService) => {
    expect(service).toBeTruthy();
  }));
});
