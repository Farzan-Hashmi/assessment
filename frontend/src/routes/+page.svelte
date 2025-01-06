<script lang="ts">
    const SERVER_URL = "http://localhost:8000";

    type Order = {
        order_number: number;
        burgers: number;
        fries: number;
        drinks: number;
    };

    let orderHistory = $state<Order[]>([]);
    let orderText = $state("");
    let totalOrders = $state({ burgers: 0, fries: 0, drinks: 0 });

    async function submitOrder() {
        console.log(orderText);

        const response = await fetch(`${SERVER_URL}/place_order`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text: orderText }),
        });
        if (!response.ok) {
            alert("Order does not exist");
        }
        orderText = "";
        fetchOrderHistory();
        fetchTotalOrders();
    }

    async function fetchOrderHistory() {
        const response = await fetch(`${SERVER_URL}/order_history`);
        orderHistory = await response.json();
    }

    async function fetchTotalOrders() {
        const response = await fetch(`${SERVER_URL}/total_orders`);
        const data = await response.json();
        totalOrders = {
            burgers: data.total_burger_orders,
            fries: data.total_fry_orders,
            drinks: data.total_drink_orders,
        };
    }

    $effect(() => {
        fetchOrderHistory();
        fetchTotalOrders();
    });
</script>

<div class="container mx-auto max-w-3xl">
    <h1 class="text-3xl font-bold text-center py-6">Order Information</h1>

    <div class="flex justify-between gap-4 mb-10 pt-4">
        <div class="text-center flex-1">
            <h3 class="text-lg font-semibold">Burgers</h3>
            <p class="text-3xl font-bold">{totalOrders.burgers}</p>
        </div>
        <div class="text-center flex-1">
            <h3 class="text-lg font-semibold">Fries</h3>
            <p class="text-3xl font-bold">{totalOrders.fries}</p>
        </div>
        <div class="text-center flex-1">
            <h3 class="text-lg font-semibold">Drinks</h3>
            <p class="text-3xl font-bold">{totalOrders.drinks}</p>
        </div>
    </div>

    <div class="flex gap-2 mb-8">
        <input
            type="text"
            bind:value={orderText}
            placeholder="Enter your order request (e.g., '3 burgers, 1 fries')"
            class="flex-1 px-3 border placeholder:text-muted-foreground"
        />
        <button
            onclick={submitOrder}
            class="h-10 px-4 py-2 bg-primary text-primary-foreground"
        >
            Submit Order
        </button>
    </div>

    <div class="space-y-4">
        <h2 class="text-xl font-semibold">Order History</h2>

        <div class="border divide-y">
            {#each orderHistory as order}
                <div class="p-4 flex justify-between items-center">
                    <p class="text-sm">Order number: {order?.order_number}</p>
                    <div class="flex flex-row gap-2">
                        <p class="text-sm">
                            {order.burgers} burgers
                        </p>
                        <p class="text-sm">
                            {order.fries} fries
                        </p>
                        <p class="text-sm">
                            {order.drinks} drinks
                        </p>
                    </div>
                </div>
            {/each}
        </div>
    </div>
</div>
