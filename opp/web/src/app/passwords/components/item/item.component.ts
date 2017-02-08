import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { MdSnackBar, MdDialog, MdDialogRef } from '@angular/material';
import { ItemFormComponent } from '../item-form/item-form.component';
import { IItem, IUpdateItemPayload } from '../../models';

@Component({
  selector: 'app-item',
  templateUrl: './item.component.html',
  styleUrls: ['./item.component.scss']
})
export class ItemComponent implements OnInit {
  @Input() item: IItem;
  @Output() updateItem = new EventEmitter<IUpdateItemPayload>(false);
  @Output() removeItem = new EventEmitter<IItem>(false);

  constructor(private dialog: MdDialog, private snackbar: MdSnackBar) { }

  ngOnInit() {
  }

  promptEdit() {
    const dialogRef = this.dialog.open(ItemFormComponent);
    dialogRef.componentInstance.item = this.item;
    dialogRef.afterClosed().subscribe((newItem: IItem) => {
      if (newItem) {
        this.updateItem.emit({
          newItem: newItem,
          initialItem: this.item
        });
      }
    });
  }

  promptDelete() {
    const dialogRef = this.dialog.open(DeleteItemDialogComponent);
    dialogRef.afterClosed().subscribe(chosenOption => {
      if (chosenOption === 'delete') {
        this.removeItem.emit(this.item);
      }
    });
  }

  copied() {
    this.snackbar.open('copied', undefined, { duration: 2000 });
  }
}

@Component({
  selector: 'app-delete-item-dialog',
  template: `
  <h1 md-dialig-title>Delete item</h1>
  <div md-dialog-content>Are you sure?</div>
  <div md-dialog-actions>
    <button md-raised-button (click)="dialogRef.close('delete')" color="warn">
      Yes, delete
    </button>
    <button md-button (click)="dialogRef.close()">Cancel</button>
  </div>
  `,
})
export class DeleteItemDialogComponent {
  constructor(public dialogRef: MdDialogRef<DeleteItemDialogComponent>) { }
}
