import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import BookDetail from '../views/BookDetail.vue'
import NotFoundPage from '../views/404.vue'

Vue.use(VueRouter)

  const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/book',
    name: 'Book',
    component: BookDetail,
  },
	{
		path: '*',
		name: '404Page',
		component: NotFoundPage
	}
]

const router = new VueRouter({
  routes
})

export default router
