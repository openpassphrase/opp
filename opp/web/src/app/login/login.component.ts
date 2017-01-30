import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MdSnackBar } from '@angular/material';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Auth } from '../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  authForm: FormGroup;

  constructor(
    private auth: Auth,
    private router: Router,
    private _fb: FormBuilder,
    private snackBar: MdSnackBar
  ) { }

  ngOnInit() {
    if (this.auth.loggedIn()) {
      this.router.navigate(['admin']);
    }
    this.authForm = this._fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  login() {
    this.auth.login(this.authForm.value).subscribe(
      // We're assuming the response will be an object
      // with the JWT on an id_token key
      data => {
        localStorage.setItem('id_token', data.access_token);
        this.router.navigate(['admin']);
      },
      error => {
        if (error.status === 401) {
          this.snackBar.open('invalid user name or password.', undefined, { duration: 6000 });
        } else {
          console.log(error);
        }
      });
  }
}
