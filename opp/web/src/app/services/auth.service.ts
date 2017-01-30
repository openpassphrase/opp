import { Injectable } from '@angular/core';
import { tokenNotExpired } from 'angular2-jwt';

@Injectable()
export class Auth {
  loggedIn() {
    return tokenNotExpired();
  }

  logout() {
    localStorage.removeItem('id_token');
  }
}
