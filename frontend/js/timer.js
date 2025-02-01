let [ seconds, minutes , hours ]= [ 0,0,0];
let timeRef = document.querySelector("#timer-display");
let int = null;


document.getElementById("start-timer").addEventListener("click",() =>{
    if (int !== null){
        clearInterval(int);
    }
    int = setInterval(displayTimer, 1000);
    
});
   

document.getElementById("pause-timer").addEventListener("click", ()=> {
        clearInterval(int);
});

document.getElementById("reset-timer").addEventListener("click",() =>{
    clearInterval(int);
    [seconds,minutes,hours] = [0,0,0];
    timeRef.innerHTML = "00 : 00: 00"
});


function displayTimer(){
    seconds++;
    if(seconds == 60){
        seconds = 0;
        minutes++;
        if (minutes == 60){
            hours++;
        }
    }
    let h = hours < 10 ? "0" + hours: hours;
    let m = minutes < 10 ? "0" + minutes: minutes;
    let s = seconds < 10 ? "0" + seconds: seconds;

    timeRef.innerHTML = `${h}  : ${m} : ${s}`;
}