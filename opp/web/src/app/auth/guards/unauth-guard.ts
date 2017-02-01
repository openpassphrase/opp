import 'rxjs/add/operator/do';
import 'rxjs/add/operator/take';

import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { CanActivate } from '@angular/router';
import { Auth } from '../services/auth.service';

@Injectable()
export class UnAuthGuard implements CanActivate {

  constructor(private auth: Auth, private router: Router) { }

  canActivate() {
    return this.auth.isLoggedIn
      .take(1)
      .map(isLoggedIn => !isLoggedIn)
      .do(isNotLoggedIn => {
        if (!isNotLoggedIn) {
          this.router.navigate(['passwords']);
        }
      });
  }
}
