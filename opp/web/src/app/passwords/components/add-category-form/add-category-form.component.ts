import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-add-category-form',
  templateUrl: './add-category-form.component.html',
  styleUrls: ['./add-category-form.component.scss']
})
export class AddCategoryFormComponent implements OnInit {
  addCategoryForm: FormGroup;
  @Output() add = new EventEmitter(false);

  constructor(private _fb: FormBuilder) { }

  ngOnInit() {
    this.addCategoryForm = this._fb.group({
      category: ['', Validators.required]
    });
  }

  addCategory() {
    if (this.addCategoryForm.valid) {
      const name = this.addCategoryForm.value.category.trim();
      this.add.emit(name);
    }
  }

  clear() {
    this.addCategoryForm.get('category').setValue('');
  }
}
