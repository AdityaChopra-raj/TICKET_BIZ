import React, { useState } from 'react';
import EventCard from './components/EventCard';
import EventDropdown from './components/EventDropdown';
import StatsCard from './components/StatsCard';
const eventsData=[{name:'Navratri Pooja',total:100,scanned:20,remaining:80,image:'/assets/navratri.jpeg'},{name:'Diwali Dance',total:150,scanned:50,remaining:100,image:'/assets/diwali.jpeg'},{name:'Freshers',total:200,scanned:80,remaining:120,image:'/assets/freshers.jpeg'},{name:'Ravan Dehan',total:120,scanned:30,remaining:90,image:'/assets/ravan_dehan.jpeg'}];
export default function App(){const [selectedEvent,setSelectedEvent]=useState(eventsData[0].name);const event=eventsData.find(e=>e.name===selectedEvent);
return (<div className='p-8'><h1 className='text-3xl font-bold mb-6'>🎟️ Event Dashboard</h1>
<EventDropdown events={eventsData} selectedEvent={selectedEvent} setSelectedEvent={setSelectedEvent}/>
<div className='flex space-x-6 mb-6'><StatsCard label='Total Tickets' stats={event.total}/><StatsCard label='Tickets Scanned' stats={event.scanned}/><StatsCard label='Tickets Remaining' stats={event.remaining}/></div>
<div className='grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6'>{eventsData.map(e=><EventCard key={e.name} event={e}/>)}</div></div>); }