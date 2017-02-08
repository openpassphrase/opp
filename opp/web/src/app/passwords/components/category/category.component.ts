import { Component, OnInit, Input, Output, EventEmitter, ViewChild, ChangeDetectionStrategy } from '@angular/core';
import { trigger, state, transition, style, animate, AnimationTransitionEvent } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MdDialog, MdDialogRef, MdTooltip } from '@angular/material';
import { ItemFormComponent } from '../item-form/item-form.component';
import {
  ICategory, IItem, ICategoryItems, IUpdateCategoryPayload,
  IRemoveCategoryPayload, IUpdateItemPayload
} from '../../models';

const speedIn = '300ms ease-in';
const speedOut = '200ms ease-out';

@Component({
  selector: 'app-category',
  templateUrl: './category.component.html',
  styleUrls: ['./category.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [
    trigger('openClose', [
      state('false, void', style({ height: '0px' })),
      state('true', style({ height: '*' })),
      transition('0 <=> 1', [animate(speedIn, style({ height: '*' })), animate(speedOut)])
    ]),
    trigger('expandForShadow', [
      state('false, void', style({ 'padding': '0 2px 1px 2px' })),
      state('true', style({ padding: '3px', margin: '12px -27px' })),
      transition('0 <=> 1', [animate(speedIn, style({ padding: '3px', margin: '10px -27px' })), animate(speedOut)])
    ]),
    trigger('offsetExpand', [
      state('false, void', style({ 'padding': '0px' })),
      state('true', style({ padding: '24px' })),
      transition('0 <=> 1', [animate(speedIn, style({ padding: '24px' })), animate(speedOut)])
    ]),
    trigger('makeHeader', [
      state('false, void', style({ 'font-size': '16px' })),
      state('true', style({ 'font-size': '30px' })),
      transition('0 <=> 1', [animate(speedIn, style({ 'font-size': '30px' })), animate(speedOut)])
    ]),
    trigger('opacityIn', [
      state('false, void', style({ opacity: 0, transform: 'scale(0.0)' })),
      state('true', style({ opacity: 1, transform: 'scale(1.0)' })),
      transition('0 <=> 1', [animate(speedIn, style({ opacity: 1, transform: 'scale(1.0)' })), animate(speedOut)])
    ])
  ]
})
export class CategoryComponent implements OnInit {
  changeCategoryForm: FormGroup;
  isInEditMode = false;

  @ViewChild('addItemTooltip', { read: MdTooltip }) addItemTooltip: MdTooltip;

  @Input() category: ICategoryItems;
  @Input() readonly isExpanded = false;
  @Output() update = new EventEmitter<IUpdateCategoryPayload>(false);
  @Output() remove = new EventEmitter<IRemoveCategoryPayload>(false);
  @Output() addItem = new EventEmitter<IItem>(false);
  @Output() updateItem = new EventEmitter<IUpdateItemPayload>(false);
  @Output() removeItem = new EventEmitter<IItem>(false);
  @Output() toggleCategoryExpanded = new EventEmitter(false);

  constructor(private _fb: FormBuilder, private dialog: MdDialog) { }

  ngOnInit() {
    this.changeCategoryForm = this._fb.group({
      newName: [this.category.name, [Validators.required, Validators.minLength(3)]]
    });
  }

  toggle() {
    this.toggleCategoryExpanded.emit(this.category.id);
  }

  toggleEditCategory() {
    this.isInEditMode = !this.isInEditMode;
  }

  saveCategoryName() {
    if (this.changeCategoryForm.valid) {
      const toSubmit: IUpdateCategoryPayload = {
        id: this.category.id,
        name: this.changeCategoryForm.value.newName,
        initialName: this.category.name
      };
      this.update.emit(toSubmit);
      this.toggleEditCategory();
    }
  }

  promptDelete() {
    const dialogRef = this.dialog.open(DeleteCategoryDialogComponent);
    dialogRef.componentInstance.hasItems = this.category.items.length > 0;
    dialogRef.afterClosed().subscribe(chosenOption => {
      if (chosenOption) {
        const cascade = chosenOption === 'deleteAll';
        this.remove.emit({ category: this.category, cascade: cascade });
      }
    });
  }

  promptAddItem() {
    const dialogRef = this.dialog.open(ItemFormComponent);
    dialogRef.componentInstance.item = { category_id: this.category.id } as any;
    dialogRef.afterClosed().subscribe(newItem => {
      if (newItem) {
        this.addItem.emit(newItem);
      }
    });
  }

  openCloseDone(ev: AnimationTransitionEvent) {
    if (ev.toState && this.category.items.length === 0) {
      this.addItemTooltip.show();
      setTimeout(() => {
        this.addItemTooltip.hide();
      }, 2000);
    }
  }
}

@Component({
  selector: 'app-delete-category-dialog',
  template: `
  <h1 md-dialig-title>Delete category</h1>
  <div md-dialog-content>Are you sure?</div>
  <div md-dialog-actions>
    <button md-raised-button (click)="dialogRef.close('deleteAll')" *ngIf="hasItems" color="warn">
      Delete category and all its belongings
    </button>
    <button md-raised-button (click)="dialogRef.close('deleteJustCategory')" color="accent">
      {{hasItems ? 'Delete category, but save all its belongings' : 'Yes, delete'}}
    </button>
    <button md-button (click)="dialogRef.close()">Cancel</button>
  </div>
  `,
})
export class DeleteCategoryDialogComponent {
  hasItems: boolean;
  constructor(public dialogRef: MdDialogRef<DeleteCategoryDialogComponent>) { }
}
