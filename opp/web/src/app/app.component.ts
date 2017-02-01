import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Auth } from './auth/auth.module';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  isLoggedIn: boolean;

  constructor(public auth: Auth, private router: Router) {
    this.auth.isLoggedIn.subscribe(newState => {
      if (!newState && this.isLoggedIn) {
        this.logout();
      }
      this.isLoggedIn = newState;
    });
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/']);
  }
}
