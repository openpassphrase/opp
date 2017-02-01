import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MdSnackBar } from '@angular/material';
import { StoreService } from '../services/store.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss']
})
export class AdminComponent implements OnInit {
  addCategoryForm: FormGroup;

  constructor(
    private store: StoreService,
    private _fb: FormBuilder,
    private snackBar: MdSnackBar
  ) { }

  ngOnInit() {
    this.addCategoryForm = this._fb.group({
      category: ['', Validators.required]
    });
  }

  addCategory() {
    if (this.addCategoryForm.valid) {
      this.store.addCategory(this.addCategoryForm.value.category)
      this.store.addCategory(this.addCategoryForm.value.category).subscribe(
        res => {

        },
        err => {
          this.snackBar.open('Could not add category', undefined, { duration: 6000 });
          console.log(err);
        }
      );
    }
  }
}
