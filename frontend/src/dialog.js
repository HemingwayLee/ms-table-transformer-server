import * as React from 'react';
import TextField from '@mui/material/TextField';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import Button from '@mui/material/Button';

const EditDialog = React.forwardRef((props, ref) => {
  const { onClose, open } = props;
  const [currText, setCurrText] = React.useState('');

  React.useImperativeHandle(ref, () => ({
    setTextFromParent(wording) {
      setCurrText(wording)
    }
  }), [setCurrText]);

  const handleClose = (isSave) => {
    onClose(isSave, currText);
  };

  const onTextAreaChange = (e) => {
    
  }

  return (
    <Dialog maxWidth="md" fullWidth={true} onClose={() => { handleClose(false); }} open={open}>
      <DialogTitle>{"Edit"}</DialogTitle>
      <TextField
        multiline
        rows={2}
        maxRows={4}
        value={currText}
        onChange={(e) => {onTextAreaChange(e)}}
      />
      <Button variant="contained" component="label" onClick={() => {handleClose(true);}}>Confirm</Button>
    </Dialog>
  );
})

export default EditDialog;
