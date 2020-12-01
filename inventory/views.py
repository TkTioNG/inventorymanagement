from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from inventory.models import Store, Material, MaterialStock, MaterialQuantity, Product
from inventory.serializers import (
    UserSerializer, StoreSerializer, MaterialSerializer, MaterialStockSerializer,
    MaterialQuantitySerializer, ProductSerializer, RestockSerializer,
    InventorySerializer, ProductCapacitySerializer, SalesSerializer
)
from inventory.utils import get_restock_total_price


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class StoreViewSet(viewsets.ModelViewSet):
    # queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_queryset(self):
        return self.request.user.stores.all()


class MaterialViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialSerializer

    def get_queryset(self):
        return Material.objects.filter(material_stocks__store__user=self.request.user)


class MaterialStockViewSet(viewsets.ModelViewSet):
    queryset = MaterialStock.objects.all()
    serializer_class = MaterialStockSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        if instance.current_capacity > data["max_capacity"]:
            raise ValidationError(
                detail="max_capacity cannot be smaller than current_capacity")
        if 'current_capacity' in data:
            del data['current_capacity']
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class MaterialQuantityViewSet(viewsets.ModelViewSet):
    queryset = MaterialQuantity.objects.all()
    serializer_class = MaterialQuantitySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class RestockViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = RestockSerializer

    def get_queryset(self):
        return MaterialStock.objects.filter(store__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer_data = self.get_serializer(queryset, many=True).data

        total_price = get_restock_total_price(serializer_data)

        data = {
            "materials": serializer_data,
            "total_price": total_price,
        }
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        materials = request.data.get('materials')
        for material in materials:
            instance = self.get_queryset().get(material=material.get('material'))
            serializer = self.get_serializer(
                instance=instance, data=material, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        return self.list(request, *args, **kwargs)


class InventoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = InventorySerializer

    def get_queryset(self):
        return MaterialStock.objects.filter(store__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        data = {
            "materials": serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)


class ProductCapacityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductCapacitySerializer

    def get_queryset(self):
        return Store.objects.get(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SalesSerializer

    def get_queryset(self):
        return Store.objects.get(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, instance=self.get_queryset())

        serializer.is_valid(raise_exception=True)

        serializer.create()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
