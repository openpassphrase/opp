import { Component, OnInit,Input } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { MdDialogRef } from '@angular/material';
import { Observable } from 'rxjs/Observable';
import { IItem } from '../../models';


@Component({
  selector: 'app-item-form',
  templateUrl: './item-form.component.html',
  styleUrls: ['./item-form.component.scss']
})
export class ItemFormComponent implements OnInit {
  @Input() item: IItem;

  saveItemForm: FormGroup;

  constructor(
    public dialogRef: MdDialogRef<ItemFormComponent>,
    private _fb: FormBuilder
  ) { }

  ngOnInit() {
    this.saveItemForm = this._fb.group({
      id: [this.item.id],
      name: [this.item.name, Validators.required],
      url: [this.item.url],
      account: [this.item.account],
      password: [this.item.password],
      blob: [this.item.blob],
      category_id: [this.item.category_id]
    });
  }

  saveItem() {
    if (this.saveItemForm.valid) {
      this.dialogRef.close(this.saveItemForm.value);
    }
  }
}
