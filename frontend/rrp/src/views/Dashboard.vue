<template>
	<div class="root">
		<Header ref="topbar"></Header>

		<!-- 404 page if there is no book_id in query -->
		<main v-if="pageNotFound">
			<NotFound></NotFound>
		</main>

		<main v-else>
			<div class="user-dashboard">
				<div class="top">
					<div class="title" v-if="isMyDashboard()">
						My dashboard - {{ account.username }}
					</div>
					<div class="title" v-else>
						User page - {{ account.username }}
					</div>
					<button class="btn-default btn-style-white animation-fadein-top delay_04s" v-if="isMyDashboard() && $route.name === 'UserCollection'" @click="$refs['collection'].openNewCollectionForm()">New Collection</button>
				</div>
				<div class="content">
					<DashboardNavi :account="account" :myAccount="myAccount"></DashboardNavi>
					
					<Collection v-if="$route.name === 'UserCollection'" ref="collection" :account="account" :myAccount="myAccount"></Collection>
				</div>
			</div>
			
		</main>

		<Footer></Footer>
	</div>
</template>

<script>
	import API_URL from '../serviceAPI.config.js'
	import Header from '../components/common/Header.vue'
	import Footer from '../components/common/Footer.vue'
	import DashboardNavi from '../components/dashboard/DashboardNavi.vue'
	import NotFound from '../components/common/NotFound.vue'
	import Collection from '../components/dashboard/Collection.vue'
	export default {
		name: 'UserCollection',
		data: function() {
			return {
				myAccount: {
					user_id: '',
					username: '',
					email: '',
					admin: ''
				},
				account: {
					user_id: '',
					username: '',
					email: '',
					admin: ''
				},
				pageNotFound: false,
			}
		},
		components: {
			Header,
			Footer,
			NotFound,
			DashboardNavi,
			Collection,
		},
		methods: {
			getAccountsInfo() {
				// if there is no user id in query -> 404
				if (this.$route.query.id === undefined) {
					this.pageNotFound = true
					return
				}
				// get page owner's info
				let userID = this.$route.query.id
				this.axios({
					method: 'get',
					url: `${API_URL}/user/${userID}/detail`,
				}).then((res) => {
					this.account = res.data
				}).catch((error) => {
					alert(error.response.data.message)
					this.pageNotFound = true
					return
				})
				// get my info (if exists)
				if (this.$store.state.token) {
					this.axios({
						method: 'get',
						url: `${API_URL}/user/detail`,
						headers: {
							'Content-Type': 'application/json',
							'AUTH-TOKEN': this.$store.state.token
						}
					}).then((res) => {
						this.myAccount = res.data
					}).catch((error) => {
						this.pageNotFound = true
						return
					})
				}
			},
			isMyDashboard() {
				return this.myAccount.user_id === this.account.user_id ? true : false
			},
		},
		mounted: function() {
			this.getAccountsInfo()
		},
	}
</script>

<style scoped>
	@import url("../assets/css/dashboard_common.css");
</style>