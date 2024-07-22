import React from 'react'
import style from './recommend.module.css'

const Recommendation = ({AiResponse}) => {
 
  const { dates, location } = AiResponse

  return (
    <div className={style.recommend}>
      <div className='heading text-xl'>Recommended Outings</div>
      {dates.map((item, index) => (
        <div key={index} className={style.outing}>
          <div className="title text-xl">Outing {index + 1}</div>
          <div className="time px-2">{item.date}</div>
          <div className="desc px-2">Location: {location[0]}</div>
        </div>
      ))}
    </div>
  )
}

export default Recommendation
