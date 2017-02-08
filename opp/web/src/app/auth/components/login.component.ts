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
    this.authForm = this._fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
      exp_delta_amount: [''],
      exp_delta_multiplier: ['']
    });

    const exp_delta_amountCtrl = this.authForm.controls['exp_delta_amount'];
    const exp_delta_multiplierCtrl = this.authForm.controls['exp_delta_multiplier'];

    exp_delta_amountCtrl.valueChanges.subscribe(newVal => {
      const notEmpty = newVal !== undefined && newVal !== null && newVal !== '';
      exp_delta_multiplierCtrl.setValidators(notEmpty ? Validators.required : null);
      exp_delta_multiplierCtrl.updateValueAndValidity({ emitEvent: false });
    });

    exp_delta_multiplierCtrl.valueChanges.subscribe(newVal => {
      const notEmpty = newVal !== undefined && newVal !== null && newVal !== '';
      exp_delta_amountCtrl.setValidators(notEmpty ? Validators.required : null);
      exp_delta_amountCtrl.updateValueAndValidity({ emitEvent: false });
    });
  }

  login() {
    if (this.authForm.valid) {
      const toSubmit = {
        username: this.authForm.value.username,
        password: this.authForm.value.password,
        exp_delta: this.authForm.value.exp_delta_amount * this.authForm.value.exp_delta_multiplier
      };
      this.auth.login(toSubmit).subscribe(
        // We're assuming the response will be an object
        // with the JWT on an id_token key
        data => {
          localStorage.setItem('id_token', data.access_token);
          this.router.navigate(['passwords']);
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
}
