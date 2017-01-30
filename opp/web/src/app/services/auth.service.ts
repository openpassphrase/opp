import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { tokenNotExpired } from 'angular2-jwt';

@Injectable()
export class Auth {
  constructor(private http: Http) { }

  loggedIn() {
    return tokenNotExpired();
  }

  login(data: { username: string, password: string }) {
    return this.http.post('/api/v1/auth', data)
      .map(res => res.json());
  }

  logout() {
    localStorage.removeItem('id_token');
  }
}
