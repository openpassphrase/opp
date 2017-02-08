import { Injectable, EventEmitter } from '@angular/core';
import { Http } from '@angular/http';
import { tokenNotExpired } from 'angular2-jwt';
import { Observable } from 'rxjs/Observable';
import { Subscriber } from 'rxjs/Subscriber';

import 'rxjs/add/observable/timer';

@Injectable()
export class Auth {
  public isLoggedIn: Observable<boolean>;

  constructor(private http: Http) {
    this.isLoggedIn = new Observable<boolean>(s => {
      Observable.timer(0, 1000).subscribe(x => {
        const token = localStorage.getItem('id_token');
        const isNotExpired = tokenNotExpired('id_token', token);
        s.next(isNotExpired);
      });
    });
  }

  login(data: { username: string, password: string }) {
    return this.http.post('/api/v1/auth', data)
      .map(res => res.json());
  }

  logout() {
    localStorage.removeItem('id_token');
  }
}
