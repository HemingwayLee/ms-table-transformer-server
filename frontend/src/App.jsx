import Button from '@mui/material/Button';
import React, { useRef }  from 'react';
import Grid from '@mui/material/Grid';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Cookies from 'js-cookie';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';

export default function Dashboard() {
  const [isBtnDisabled, setBtnDisabled] = React.useState(false);
  const [isDropDownDisabled, setDropDownDisabled] = React.useState(false);
  const [fileList, setFileList] = React.useState([]);
  const [selectedImg, setSelectedImg] = React.useState('');
  const [selectedIdx, setSelectedIdx] = React.useState(0);
  const [isResultReady, setResultReady] = React.useState(false);
  const [res, setRes] = React.useState('');
  const canvasRef = React.useRef(null);

  const handleSelectedImage = async (filename) => {
    setSelectedImg(filename);

    var background = new Image();
    background.src = `media/images/${filename}`;

    background.onload = function() {
      canvasRef.current.width = background.width;
      canvasRef.current.height = background.height;
      
      const context = canvasRef.current.getContext('2d');
      context.drawImage(background,0,0);   

      doPrediction(filename);
    }
  }
  
  // const fetchResImage = async () => {
  //   const res = await fetch(`media/results/${selectedImg}`);
  //   const imageBlob = await res.blob();
  //   const imageObjectURL = URL.createObjectURL(imageBlob);
  //   setRes(imageObjectURL);
  //   setResultReady(true);
  // };

  React.useEffect(() => {
    getData();
  }, []);

  // const cleanup = () => {
  //   fetch(`/api/clean/`, {
  //     method: 'POST',
  //     headers: { 
  //       'Content-Type': 'application/json',
  //       'X-CSRFToken': Cookies.get('csrftoken'),
  //     }
  //   })
  //   .then(function(response) {
  //     if (response.status === 200) {
  //       console.log(response.json());
  //     } else {
  //       alert("backend errors")
  //     }
  //   });
  // }

  const drawBboxes = (bboxes) => {
    for (var i=0; i<bboxes.length; ++i) {
      // console.log(bboxes[i]["bbox"]);
      const context = canvasRef.current.getContext('2d');
      context.strokeStyle = "red";
      context.beginPath();
      context.rect(
        bboxes[i]["bbox"][0], 
        bboxes[i]["bbox"][1], 
        bboxes[i]["bbox"][2], 
        bboxes[i]["bbox"][3]
      );
      context.stroke();
    }
  }

  const getData = async () => {
    const url = `/api/list/images/`
    try {
      const response = await fetch(url);
      if (response.statusText === 'OK') {
        const data = await response.json();
        console.log(data);
        setFileList(data.images.map((x, idx) => {
          return {
            "img": x,
            "id": idx
          }
        }));
        setSelectedIdx(0)
        handleSelectedImage((data.images.length > 0) ? data.images[0] : '' )
      } else {
        throw new Error('Request failed')
      }
    } catch (error) {
      console.log(error);
    }
  }

  const doPrediction = (filename) => {
    // console.log(e);
    // console.log(e.getDataURL())
    // console.log(e.getSaveData());
    setBtnDisabled(true);
    setDropDownDisabled(true);

    fetch(`/api/predict/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      body: JSON.stringify({
        filename: filename
      })
    })
    .then(function(response) {
      setBtnDisabled(false);
      setDropDownDisabled(false);

      if (response.status === 200) {
        return response.json();
      } else {
        alert("backend errors")
      }
    })
    .then(function(myJson) {
      // fetchResImage()
      // getData();
      console.log(myJson["result"])
      drawBboxes(myJson["result"]);
    });
  }

  const handleDropDownChange = (e) => {
    // cleanup();
    setResultReady(false);
    setSelectedIdx(e.target.value);
    handleSelectedImage(fileList.filter(x=>x.id == e.target.value)[0].img);
  }

  const handleImgLoad = ({target}) => {
    if (target.files.length < 1) {
      return
    }

    const selectedFile = target.files[0];
    // const url = URL.createObjectURL(selectedFile)

    if (selectedFile) {
      let data = new FormData();
      data.append('myfile', selectedFile);
      fetch(`/api/upload/`, {
        method: 'POST',
        headers: { 
          // make sure NOT to set Content-Type, browser will set for you
          // 'Content-Type': 'multipart/form-data',
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
        body: data
      })
      .then(function(response) {
        if (response.status === 200) {
          return response.json();
        } else {
          alert("backend errors")
        }
      })
      .then(function(myJson) {
        alert(myJson["result"]);
        getData();
      });
    }
  }
  
  return (
      <Box sx={{ display: 'flex' }}>
        {/* <Box
          component="main"
          sx={{
            backgroundColor: '#AAAAAA',
            flexGrow: 1,
            height: '100vh',
            overflow: 'auto',
          }}
        > */}
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
                  <InputLabel variant="standard" htmlFor="uncontrolled-native">
                    Existing images
                  </InputLabel>
                  <Select
                    labelId="img-select-label"
                    id="img-select"
                    value={selectedIdx}
                    label="selectOption"
                    onChange={handleDropDownChange}
                    disabled={isDropDownDisabled}
                  >
                    {
                      fileList.map(x => (
                        <MenuItem key={`menu-${x.id}`} value={x.id}>{x.img}</MenuItem>
                      ))
                    }
                  </Select>
                  <hr />
                  <Button variant="contained" component="label" onChange={handleImgLoad} disabled={isBtnDisabled}>
                    Load your file
                    <input type="file" accept=".jpg, .jpeg, .png, .bmp" hidden />
                  </Button>
                </Paper>
              </Grid>
              <Grid item xs={12}>
                <Paper sx={{ p: 2, overflowX: "auto", overflowY: "hidden" }}>
                  <table>
                    <thead>
                      <tr>
                        <td>Image</td>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>
                          <canvas
                            ref={canvasRef} 
                          />
                          </td>
                      </tr>
                      {/* <tr>
                        <td>Result</td>
                      </tr>
                      <tr>
                        <td>
                          {
                            isResultReady && (
                              <img src={res} width="330" height="330"/>
                            )
                          }
                        </td>
                      </tr> */}
                    </tbody>
                  </table>
                </Paper>
              </Grid>
              {/* <Grid item xs={12}>
                <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
                  <Button variant="contained" component="label">Init database from TRANS.txt</Button>
                </Paper>
              </Grid> */}
            </Grid>
          </Container>
        {/* </Box> */}
      </Box>
  );
}
