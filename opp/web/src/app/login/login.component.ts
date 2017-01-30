import { Component, OnInit } from '@angular/core';
import { Http } from '@angular/http';
import { Router } from '@angular/router';
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
    private http: Http,
    private auth: Auth,
    private router: Router,
    private _fb: FormBuilder
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
    const url = 'http://192.168.1.15:5000/api/v1/auth';
    console.log(url);
    this.http.post(url, this.authForm.value)
      .map(res => res.json())
      .subscribe(
        // We're assuming the response will be an object
        // with the JWT on an id_token key
        data => localStorage.setItem('id_token', data.access_token),
        error => console.log(error)
      );
  }
}
