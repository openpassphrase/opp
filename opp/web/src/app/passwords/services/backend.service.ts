import { Injectable } from '@angular/core';
import { AuthHttp } from 'angular2-jwt';

@Injectable()
export class BackendService {

  constructor(private http: AuthHttp) { }

  fetchAll() {
    return this.http.get('/api/v1/fetchall')
      .map(res => res.json());
  }

  addCategory(name: string) {
    return this.http.put('/api/v1/categories', [name])
      .map(res => res.json());
  }
}
